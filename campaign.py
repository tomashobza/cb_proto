import random
from dataclasses import dataclass
from typing import Literal

from arc import Arc, ArcError
from scenario import Scenario


@dataclass(frozen=True)
class CampaignArc:
  id: str
  arc: Arc
  promotion: bool = False
  available_from_turn: int = 1


@dataclass(frozen=True)
class FillerEvent:
  id: str
  title: str
  scenario: Scenario
  actor_names: tuple[str, ...]


@dataclass(frozen=True)
class InboxItem:
  id: str
  title: str
  kind: Literal["active_arc", "new_arc", "filler"]
  summary: str


@dataclass(frozen=True)
class PresentedDecision:
  index: int
  description: str
  tags: tuple[str, ...]


@dataclass(frozen=True)
class PresentedScene:
  item_id: str
  title: str
  description: str
  actors: tuple[tuple[str, str], ...]
  decisions: tuple[PresentedDecision, ...]

  @property
  def requires_decision(self):
    return bool(self.decisions)


@dataclass(frozen=True)
class StatChange:
  subject: str
  stat: str
  before: float
  after: float

  @property
  def delta(self):
    return self.after - self.before


@dataclass(frozen=True)
class TurnResult:
  turn: int
  title: str
  choice: str | None
  changes: tuple[StatChange, ...]
  arc_completed: str | None = None
  promoted_to: str | None = None


class GameSession:
  def __init__(
    self,
    player,
    npcs,
    arcs,
    fillers,
    *,
    max_turns=12,
    max_active_arcs=2,
    seed=7,
  ):
    self.player = player
    self.npcs = list(npcs)
    self.arcs = {arc.id: arc for arc in arcs}
    self.fillers = {filler.id: filler for filler in fillers}
    self.max_turns = max_turns
    self.max_active_arcs = max_active_arcs
    self.turn = 1
    self.history = []

    self._rng = random.Random(seed)
    self._inbox = None
    self._selected = None
    self._last_filler_id = None
    self._started_arc_ids = set()
    self._completed_arc_ids = set()

  @property
  def is_over(self):
    return self.turn > self.max_turns

  @property
  def active_arcs(self):
    return tuple(
      campaign_arc
      for campaign_arc in self.arcs.values()
      if campaign_arc.arc.is_active
    )

  @property
  def completed_arcs(self):
    return tuple(
      self.arcs[arc_id]
      for arc_id in self.arcs
      if arc_id in self._completed_arc_ids
    )

  @property
  def selected_scene(self):
    if self._selected is None:
      return None
    return self._present_selected()

  def available_actions(self):
    if self.is_over:
      return ()
    if self._inbox is None:
      self._inbox = tuple(self._build_inbox())
    return self._inbox

  def select_inbox_item(self, item_id):
    if self._selected is not None:
      raise RuntimeError("Resolve the current scene before selecting another")

    item = next(
      (candidate for candidate in self.available_actions() if candidate.id == item_id),
      None,
    )
    if item is None:
      raise ValueError(f"Unknown inbox item: {item_id}")

    if item.kind == "filler":
      self._selected = (item, self.fillers[item.id])
    else:
      campaign_arc = self.arcs[item.id]
      if item.kind == "new_arc":
        campaign_arc.arc.start(self.player, self.npcs, rng=self._rng)
        self._started_arc_ids.add(item.id)
      self._selected = (item, campaign_arc)
    return self._present_selected()

  def resolve_current(self, decision_index=None):
    if self._selected is None:
      raise RuntimeError("No scene is currently selected")

    item, content = self._selected
    scene = self._scenario_for(content)
    if scene.decisions:
      if (
        not isinstance(decision_index, int)
        or isinstance(decision_index, bool)
        or decision_index < 0
        or decision_index >= len(scene.decisions)
      ):
        raise ValueError(
          f"Decision index must be between 0 and {len(scene.decisions) - 1}"
        )
      choice = scene.decisions[decision_index].description
    else:
      if decision_index is not None:
        raise ValueError("This scene does not accept a decision")
      choice = None

    before = self._snapshot()
    completed_arc = None
    promoted_to = None

    if item.kind == "filler":
      actors = [self._npc_by_name(name) for name in content.actor_names]
      scene.play(self.player, actors, decision_index)
      self._last_filler_id = content.id
    else:
      arc = content.arc
      if scene.decisions:
        arc.choose(decision_index)
      else:
        arc.advance()
      if arc.completed:
        completed_arc = arc.name
        self._completed_arc_ids.add(content.id)
        if content.promotion and self._promotion_succeeded(arc):
          promoted_to = self.player.promote().value

    changes = self._changes_since(before)
    result = TurnResult(
      turn=self.turn,
      title=item.title,
      choice=choice,
      changes=changes,
      arc_completed=completed_arc,
      promoted_to=promoted_to,
    )
    self.history.append(result)
    self.turn += 1
    self._selected = None
    self._inbox = None
    return result

  def final_rating(self):
    if self.player.level > 0:
      return "Exceeds Expectations (Pending Budget)"
    if self.player.stress.get_value() >= 0.8:
      return "Unsustainable High Performer"
    if self.player.reputation.get_value() >= 0.5:
      return "Strong Contributor, Not Yet Visible Enough"
    return "Meets Expectations"

  def _build_inbox(self):
    items = []
    for campaign_arc in self.active_arcs:
      items.append(InboxItem(
        id=campaign_arc.id,
        title=campaign_arc.arc.name,
        kind="active_arc",
        summary=campaign_arc.arc.current_scenario.description,
      ))

    if len(self.active_arcs) < self.max_active_arcs:
      for campaign_arc in self.arcs.values():
        if campaign_arc.id in self._started_arc_ids:
          continue
        if self.turn < campaign_arc.available_from_turn:
          continue
        if campaign_arc.arc.is_available(self.player, self.npcs):
          items.append(InboxItem(
            id=campaign_arc.id,
            title=campaign_arc.arc.name,
            kind="new_arc",
            summary=campaign_arc.arc.current_scenario.description
            if campaign_arc.arc.current_scenario
            else campaign_arc.arc.scenarios[
              campaign_arc.arc.start_scenario_id
            ].description,
          ))

    filler_pool = list(self.fillers.values())
    if len(filler_pool) > 2 and self._last_filler_id is not None:
      filler_pool = [
        filler for filler in filler_pool
        if filler.id != self._last_filler_id
      ]
    for filler in self._rng.sample(filler_pool, min(2, len(filler_pool))):
      items.append(InboxItem(
        id=filler.id,
        title=filler.title,
        kind="filler",
        summary=filler.scenario.description,
      ))
    return items

  def _present_selected(self):
    item, content = self._selected
    scenario = self._scenario_for(content)
    if item.kind == "filler":
      actors = tuple(("coworker", name) for name in content.actor_names)
    else:
      actors = tuple(
        (role, npc.name)
        for role, npc in content.arc.actors.items()
      )
    decisions = tuple(
      PresentedDecision(
        index=index,
        description=decision.description,
        tags=tuple(tag.value for tag in decision.tags),
      )
      for index, decision in enumerate(scenario.decisions)
    )
    return PresentedScene(
      item_id=item.id,
      title=item.title,
      description=scenario.description,
      actors=actors,
      decisions=decisions,
    )

  @staticmethod
  def _scenario_for(content):
    if isinstance(content, FillerEvent):
      return content.scenario
    return content.arc.current_scenario

  def _npc_by_name(self, name):
    for npc in self.npcs:
      if npc.name == name:
        return npc
    raise ValueError(f"Unknown NPC: {name}")

  def _snapshot(self):
    snapshot = {
      self.player.name: {
        "Reputation": self.player.reputation.get_value(),
        "Political Capital": self.player.political_capital.get_value(),
        "Stress": self.player.stress.get_value(),
      },
    }
    for npc in self.npcs:
      snapshot[npc.name] = {
        "Warmth": npc.warmth.get_value(),
        "Respect": npc.respect.get_value(),
      }
    return snapshot

  def _changes_since(self, before):
    after = self._snapshot()
    changes = []
    for subject, stats in before.items():
      for stat, old_value in stats.items():
        new_value = after[subject][stat]
        if new_value != old_value:
          changes.append(StatChange(subject, stat, old_value, new_value))
    return tuple(changes)

  @staticmethod
  def _promotion_succeeded(arc):
    return any(
      isinstance(entry.payload, dict)
      and entry.payload.get("promotion") is True
      for entry in arc.history
    )
