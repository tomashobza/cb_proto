import operator
import random
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Callable

from archetypes import ArchetypesEnum
from org_chart import OrgRole, normalize_level, normalize_role
from scenario import Scenario


COMPARISON_OPERATORS = {
  "<": operator.lt,
  "<=": operator.le,
  "==": operator.eq,
  "!=": operator.ne,
  ">=": operator.ge,
  ">": operator.gt,
}

PLAYER_VALUES = {
  "reputation": lambda player: player.reputation.get_value(),
  "political_capital": lambda player: player.political_capital.get_value(),
  "stress": lambda player: player.stress.get_value(),
  "level": lambda player: player.level,
}


@dataclass(frozen=True)
class PlayerCondition:
  stat: str
  comparison: str
  value: float | int | OrgRole | str

  def __post_init__(self):
    if self.stat not in PLAYER_VALUES:
      raise ValueError(f"Unknown player value: {self.stat}")
    if self.comparison not in COMPARISON_OPERATORS:
      raise ValueError(f"Unknown comparison operator: {self.comparison}")
    if self.stat == "level":
      object.__setattr__(self, "value", normalize_level(self.value))

  def matches(self, player) -> bool:
    value = PLAYER_VALUES[self.stat](player)
    return COMPARISON_OPERATORS[self.comparison](value, self.value)


@dataclass(frozen=True)
class ActorQuery:
  archetypes: frozenset[ArchetypesEnum] | None = None
  roles: frozenset[OrgRole] | None = None
  role_level: tuple[int | OrgRole | str, int | OrgRole | str] | None = None
  warmth: tuple[float, float] | None = None
  respect: tuple[float, float] | None = None

  def __post_init__(self):
    if self.archetypes is not None:
      object.__setattr__(self, "archetypes", frozenset(self.archetypes))
    if self.roles is not None:
      object.__setattr__(
        self,
        "roles",
        frozenset(normalize_role(role) for role in self.roles),
      )
    if self.role_level is not None:
      object.__setattr__(
        self,
        "role_level",
        tuple(self._normalize_level(value) for value in self.role_level),
      )
    self._validate_range("warmth", self.warmth)
    self._validate_range("respect", self.respect)
    self._validate_range("role_level", self.role_level)

  @staticmethod
  def _normalize_level(value):
    return normalize_level(value)

  @staticmethod
  def _validate_range(name, value_range):
    if value_range is None:
      return
    if len(value_range) != 2 or value_range[0] > value_range[1]:
      raise ValueError(f"{name} must be a (minimum, maximum) tuple")

  def matches(self, npc) -> bool:
    if self.archetypes is not None and npc.archetype not in self.archetypes:
      return False
    if self.roles is not None and npc.role not in self.roles:
      return False
    if not self._stat_matches(npc.level, self.role_level):
      return False
    if not self._stat_matches(npc.warmth.get_value(), self.warmth):
      return False
    if not self._stat_matches(npc.respect.get_value(), self.respect):
      return False
    return not npc.is_locked

  @staticmethod
  def _stat_matches(value, value_range):
    return value_range is None or value_range[0] <= value <= value_range[1]


@dataclass(frozen=True)
class ArcHistoryEntry:
  scenario_id: str
  decision_index: int | None
  tags: tuple
  payload: Any


@dataclass(frozen=True)
class ArcState:
  current_scenario_id: str | None
  actors: MappingProxyType
  history: tuple[ArcHistoryEntry, ...]
  completed: bool


class ArcError(RuntimeError):
  pass


class ArcTransitionError(ArcError):
  pass


TransitionResolver = Callable[[ArcState, Any], str | None]


class Arc:
  def __init__(
    self,
    name: str,
    scenarios: dict[str, Scenario],
    start_scenario_id: str,
    actor_queries: dict[str, ActorQuery] | None = None,
    conditions: tuple[PlayerCondition, ...] = (),
    transitions: dict[str, str | None | TransitionResolver] | None = None,
  ):
    if not scenarios:
      raise ValueError("An arc must contain at least one scenario")
    if start_scenario_id not in scenarios:
      raise ValueError(f"Unknown start scenario: {start_scenario_id}")

    self.name = name
    self.scenarios = dict(scenarios)
    self.start_scenario_id = start_scenario_id
    self.actor_queries = dict(actor_queries or {})
    self.conditions = tuple(conditions)
    self.transitions = dict(transitions or {})

    self._validate_configuration()
    self._reset_runtime()

  @property
  def is_active(self):
    return self._active

  @property
  def completed(self):
    return self._completed

  @property
  def current_scenario(self):
    if self.current_scenario_id is None:
      return None
    return self.scenarios[self.current_scenario_id]

  @property
  def actors(self):
    return MappingProxyType(self._actors)

  @property
  def history(self):
    return tuple(self._history)

  @property
  def state(self):
    return ArcState(
      current_scenario_id=self.current_scenario_id,
      actors=MappingProxyType(dict(self._actors)),
      history=tuple(self._history),
      completed=self._completed,
    )

  def is_available(self, player, npcs) -> bool:
    if self._active:
      return False
    if not all(condition.matches(player) for condition in self.conditions):
      return False
    return self._find_cast(list(npcs), random.Random(0)) is not None

  def start(self, player, npcs, rng=None):
    if self._active:
      raise ArcError("Arc is already active")
    if not all(condition.matches(player) for condition in self.conditions):
      raise ArcError("Player does not meet this arc's conditions")

    cast = self._find_cast(list(npcs), rng or random.Random())
    if cast is None:
      raise ArcError("No valid cast is available for this arc")

    locked = []
    try:
      for npc in cast.values():
        npc.lock_for(self)
        locked.append(npc)
    except Exception:
      for npc in locked:
        npc.unlock_for(self)
      raise

    self._player = player
    self._actors = cast
    self._history = []
    self.current_scenario_id = self.start_scenario_id
    self._active = True
    self._completed = False
    return self.current_scenario

  def choose(self, decision_index):
    self._require_active()
    scenario = self.current_scenario
    if not scenario.decisions:
      raise ArcError("Current scenario has no decisions; call advance()")

    if (
      not isinstance(decision_index, int)
      or isinstance(decision_index, bool)
      or decision_index < 0
      or decision_index >= len(scenario.decisions)
    ):
      raise ValueError(
        f"Decision index must be between 0 and {len(scenario.decisions) - 1}"
      )

    decision = scenario.decisions[decision_index]
    payload = scenario.play(self._player, self._actors, decision_index)
    self._history.append(ArcHistoryEntry(
      scenario_id=self.current_scenario_id,
      decision_index=decision_index,
      tags=tuple(decision.tags),
      payload=payload,
    ))
    self._transition(payload)
    return payload

  def advance(self):
    self._require_active()
    scenario = self.current_scenario
    if scenario.decisions:
      raise ArcError("Current scenario requires a decision; call choose()")

    payload = scenario.play(self._player, self._actors)
    self._history.append(ArcHistoryEntry(
      scenario_id=self.current_scenario_id,
      decision_index=None,
      tags=(),
      payload=payload,
    ))
    self._transition(payload)
    return payload

  def abort(self):
    if not self._active:
      return
    self._release_actors()
    self._active = False
    self.current_scenario_id = None

  def _transition(self, payload):
    source_id = self.current_scenario_id
    transition = self.transitions.get(source_id)

    try:
      target = transition(self.state, payload) if callable(transition) else transition
      if target is not None and target not in self.scenarios:
        raise ArcTransitionError(
          f"Transition from {source_id} targets unknown scenario {target}"
        )
    except Exception as error:
      self.abort()
      if isinstance(error, ArcTransitionError):
        raise
      raise ArcTransitionError(
        f"Transition from {source_id} failed"
      ) from error

    if target is None:
      self._release_actors()
      self.current_scenario_id = None
      self._active = False
      self._completed = True
    else:
      self.current_scenario_id = target

  def _find_cast(self, npcs, rng):
    roles = list(self.actor_queries)
    candidates = {
      role: [npc for npc in npcs if query.matches(npc)]
      for role, query in self.actor_queries.items()
    }
    if any(not matches for matches in candidates.values()):
      return None

    roles.sort(key=lambda role: len(candidates[role]))
    for matches in candidates.values():
      rng.shuffle(matches)

    def assign(index, cast, used_ids):
      if index == len(roles):
        return dict(cast)

      role = roles[index]
      for npc in candidates[role]:
        if id(npc) in used_ids:
          continue
        cast[role] = npc
        result = assign(index + 1, cast, used_ids | {id(npc)})
        if result is not None:
          return result
      cast.pop(role, None)
      return None

    return assign(0, {}, set())

  def _release_actors(self):
    for npc in self._actors.values():
      npc.unlock_for(self)

  def _require_active(self):
    if not self._active:
      raise ArcError("Arc is not active")

  def _validate_configuration(self):
    unknown_transition_sources = set(self.transitions) - set(self.scenarios)
    if unknown_transition_sources:
      raise ValueError(
        f"Transitions reference unknown scenarios: {unknown_transition_sources}"
      )

    for source, target in self.transitions.items():
      if isinstance(target, str) and target not in self.scenarios:
        raise ValueError(
          f"Transition from {source} targets unknown scenario {target}"
        )
      if target is not None and not isinstance(target, str) and not callable(target):
        raise TypeError(f"Invalid transition for scenario {source}")

    declared_roles = set(self.actor_queries)
    for scenario_id, scenario in self.scenarios.items():
      unknown_roles = set(scenario.actor_roles) - declared_roles
      if unknown_roles:
        raise ValueError(
          f"Scenario {scenario_id} uses undeclared actor roles: {unknown_roles}"
        )

  def _reset_runtime(self):
    self._player = None
    self._actors = {}
    self._history = []
    self.current_scenario_id = None
    self._active = False
    self._completed = False
