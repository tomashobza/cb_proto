import random
import unittest

from arc import (
  ActorQuery,
  Arc,
  ArcError,
  ArcTransitionError,
  PlayerCondition,
)
from archetypes import ArchetypesEnum
from decision import Decision
from npc import NPC
from org_chart import OrgRole
from player import Player
from scenario import Scenario
from tags import TagEnum


def four_decisions(payload=None):
  return tuple(
    Decision(f"Choice {index}", [TagEnum.HONEST], return_data=payload)
    for index in range(4)
  )


class ScenarioTests(unittest.TestCase):
  def test_standalone_scenario_applies_tags_and_returns_payload(self):
    player = Player("Player")
    npc = NPC("Mentor", ArchetypesEnum.Mentor)
    payload = {"branch": "honest"}
    scenario = Scenario("Filler", four_decisions(payload))

    result = scenario.play(player, [npc], 0)

    self.assertIs(result, payload)
    self.assertAlmostEqual(player.reputation.get_value(), 0.2)
    self.assertAlmostEqual(npc.warmth.get_value(), 0.3)

  def test_scenario_execution_modes_are_validated(self):
    player = Player("Player")
    no_decision = Scenario("Setup")
    with_decision = Scenario("Dilemma", four_decisions())

    with self.assertRaises(ValueError):
      no_decision.play(player, [], 0)
    with self.assertRaises(ValueError):
      with_decision.play(player, [])


class QueryTests(unittest.TestCase):
  def test_player_condition_comparisons_include_boundaries(self):
    player = Player("Player")
    player.set_stat("Reputation", 0.5)

    self.assertTrue(PlayerCondition("reputation", ">=", 0.5).matches(player))
    self.assertTrue(PlayerCondition("reputation", "<=", 0.5).matches(player))
    self.assertTrue(PlayerCondition("reputation", "==", 0.5).matches(player))
    self.assertFalse(PlayerCondition("reputation", ">", 0.5).matches(player))
    self.assertFalse(PlayerCondition("reputation", "<", 0.5).matches(player))
    self.assertFalse(PlayerCondition("reputation", "!=", 0.5).matches(player))

  def test_player_condition_can_require_org_level(self):
    player = Player("Player")

    self.assertTrue(PlayerCondition("level", "==", OrgRole.INTERN).matches(player))
    self.assertTrue(PlayerCondition("level", "==", 0).matches(player))
    self.assertTrue(PlayerCondition("level", "==", "intern").matches(player))
    self.assertFalse(PlayerCondition("level", ">=", OrgRole.MANAGER).matches(player))

    player.set_role(OrgRole.MANAGER)

    self.assertTrue(PlayerCondition("level", ">=", OrgRole.MANAGER).matches(player))
    self.assertTrue(PlayerCondition("level", ">=", 3).matches(player))

  def test_actor_query_filters_archetype_stats_and_locks(self):
    npc = NPC("Mentor", ArchetypesEnum.Mentor)
    npc.warmth.set_value(0.4)
    npc.respect.set_value(0.2)
    query = ActorQuery(
      archetypes={ArchetypesEnum.Mentor},
      warmth=(0.3, 0.5),
      respect=(0.2, 0.6),
    )

    self.assertTrue(query.matches(npc))
    npc.lock_for(object())
    self.assertFalse(query.matches(npc))

  def test_actor_query_filters_org_roles_and_role_levels(self):
    manager = NPC("Manager", ArchetypesEnum.Bureaucrat, role="manager")
    associate = NPC("Associate", ArchetypesEnum.Mentor, role=OrgRole.ASSOCIATE)
    manager_query = ActorQuery(
      roles={OrgRole.MANAGER},
      role_level=(OrgRole.MANAGER, OrgRole.DIRECTOR),
    )

    self.assertTrue(manager_query.matches(manager))
    self.assertFalse(manager_query.matches(associate))


class OrgChartTests(unittest.TestCase):
  def test_player_starts_as_intern_and_promotes_through_progression(self):
    player = Player("Player")

    self.assertEqual(player.role, OrgRole.INTERN)
    self.assertEqual(player.promote(), OrgRole.ASSOCIATE)
    self.assertEqual(player.role, OrgRole.ASSOCIATE)


class ArcTests(unittest.TestCase):
  def setUp(self):
    self.player = Player("Player")
    self.mentor = NPC("Morgan", ArchetypesEnum.Mentor, role=OrgRole.MANAGER)
    self.climber = NPC("Casey", ArchetypesEnum.LadderClimber, role=OrgRole.ASSOCIATE)
    self.setup = Scenario("Setup", actor_roles=("lead",))
    self.dilemma = Scenario(
      "Dilemma",
      four_decisions({"route": "good"}),
      actor_roles=("lead",),
    )
    self.aftermath = Scenario("Aftermath", actor_roles=("lead",))

  def make_arc(self, **overrides):
    arguments = {
      "name": "Test Arc",
      "scenarios": {
        "setup": self.setup,
        "dilemma": self.dilemma,
        "aftermath": self.aftermath,
      },
      "start_scenario_id": "setup",
      "actor_queries": {
        "lead": ActorQuery(
          archetypes={ArchetypesEnum.Mentor},
          role_level=(OrgRole.MANAGER, OrgRole.C_SUITE),
        ),
      },
      "conditions": (PlayerCondition("stress", "<=", 0),),
      "transitions": {
        "setup": "dilemma",
        "dilemma": lambda state, payload: (
          "aftermath"
          if state.history[-1].payload == payload
          and payload["route"] == "good"
          else None
        ),
      },
    }
    arguments.update(overrides)
    return Arc(**arguments)

  def test_casting_branching_history_completion_and_unlock(self):
    arc = self.make_arc()

    self.assertTrue(arc.is_available(self.player, [self.climber, self.mentor]))
    arc.start(
      self.player,
      [self.climber, self.mentor],
      rng=random.Random(4),
    )
    self.assertIs(arc.actors["lead"], self.mentor)
    self.assertTrue(self.mentor.is_locked)

    arc.advance()
    payload = arc.choose(0)
    self.assertEqual(payload, {"route": "good"})
    self.assertEqual(arc.current_scenario_id, "aftermath")
    self.assertEqual(len(arc.history), 2)
    self.assertEqual(arc.history[-1].decision_index, 0)
    self.assertEqual(arc.history[-1].tags, (TagEnum.HONEST,))

    arc.advance()
    self.assertTrue(arc.completed)
    self.assertFalse(arc.is_active)
    self.assertFalse(self.mentor.is_locked)

  def test_casting_requires_distinct_npcs_and_leaves_no_partial_locks(self):
    arc = self.make_arc(
      actor_queries={
        "lead": ActorQuery(archetypes={ArchetypesEnum.Mentor}),
        "advisor": ActorQuery(archetypes={ArchetypesEnum.Mentor}),
      },
      scenarios={
        "setup": Scenario("Setup", actor_roles=("lead", "advisor")),
      },
      transitions={},
    )

    self.assertFalse(arc.is_available(self.player, [self.mentor]))
    with self.assertRaises(ArcError):
      arc.start(self.player, [self.mentor])
    self.assertFalse(self.mentor.is_locked)

  def test_locked_actor_cannot_join_a_second_arc(self):
    first = self.make_arc()
    second = self.make_arc()
    first.start(self.player, [self.mentor])

    self.assertFalse(second.is_available(self.player, [self.mentor]))
    with self.assertRaises(ArcError):
      second.start(self.player, [self.mentor])
    first.abort()
    self.assertFalse(self.mentor.is_locked)

  def test_conditions_prevent_start(self):
    self.player.set_stat("Stress", 0.5)
    arc = self.make_arc()

    self.assertFalse(arc.is_available(self.player, [self.mentor]))
    with self.assertRaises(ArcError):
      arc.start(self.player, [self.mentor])

  def test_invalid_lifecycle_calls_raise_clear_errors(self):
    arc = self.make_arc()
    with self.assertRaisesRegex(ArcError, "not active"):
      arc.advance()

    arc.start(self.player, [self.mentor])
    with self.assertRaisesRegex(ArcError, "no decisions"):
      arc.choose(0)
    arc.advance()
    with self.assertRaisesRegex(ArcError, "requires a decision"):
      arc.advance()
    with self.assertRaises(ValueError):
      arc.choose(9)
    with self.assertRaises(ValueError):
      arc.choose("0")

  def test_transition_failure_aborts_and_unlocks(self):
    def broken_transition(state, payload):
      del state, payload
      raise RuntimeError("broken")

    arc = self.make_arc(transitions={"setup": broken_transition})
    arc.start(self.player, [self.mentor])

    with self.assertRaisesRegex(ArcTransitionError, "setup failed"):
      arc.advance()
    self.assertFalse(arc.is_active)
    self.assertFalse(self.mentor.is_locked)

  def test_unknown_dynamic_transition_aborts_and_unlocks(self):
    arc = self.make_arc(
      transitions={"setup": lambda state, payload: "missing"}
    )
    arc.start(self.player, [self.mentor])

    with self.assertRaisesRegex(ArcTransitionError, "unknown scenario"):
      arc.advance()
    self.assertFalse(self.mentor.is_locked)

  def test_unknown_static_transition_is_rejected_during_configuration(self):
    with self.assertRaisesRegex(ValueError, "unknown scenario"):
      self.make_arc(transitions={"setup": "missing"})


if __name__ == "__main__":
  unittest.main()
