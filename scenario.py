from collections.abc import Mapping, Sequence

from decision import Decision


class Scenario:
  def __init__(
    self,
    description: str,
    decisions: Sequence[Decision] = (),
    actor_roles: Sequence[str] = (),
  ):
    if len(decisions) not in (0, 4):
      raise ValueError("A scenario must have either zero or four decisions")
    if len(set(actor_roles)) != len(actor_roles):
      raise ValueError("Scenario actor roles must be unique")

    self.description = description
    self.decisions = tuple(decisions)
    self.actor_roles = tuple(actor_roles)

  def __str__(self):
    if not self.decisions:
      return self.description

    choices = "\n".join(
      f"{index}. {decision}"
      for index, decision in enumerate(self.decisions, start=1)
    )
    return f"{self.description}\n\n{choices}"

  def play(self, player, actors, decision_index=None):
    resolved_actors = self._resolve_actors(actors)

    if not self.decisions:
      if decision_index is not None:
        raise ValueError("This scenario does not accept a decision")
      return None

    if (
      not isinstance(decision_index, int)
      or isinstance(decision_index, bool)
      or decision_index < 0
      or decision_index >= len(self.decisions)
    ):
      raise ValueError(
        f"Decision index must be between 0 and {len(self.decisions) - 1}"
      )

    decision = self.decisions[decision_index]
    tags = decision.choose()

    for actor in resolved_actors:
      actor.affect_by_tags(tags)
    player.affect_by_tags(tags)

    return decision.get_return_data()

  def _resolve_actors(self, actors):
    if isinstance(actors, Mapping):
      missing_roles = [
        role for role in self.actor_roles
        if role not in actors
      ]
      if missing_roles:
        raise ValueError(
          f"Missing actors for roles: {', '.join(missing_roles)}"
        )
      return [actors[role] for role in self.actor_roles]

    if self.actor_roles:
      raise ValueError("Role-based scenarios require an actor mapping")

    return list(actors)
