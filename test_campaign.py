import unittest

from content import create_game_session


def item_by_kind(session, kind):
  return next(item for item in session.available_actions() if item.kind == kind)


class GameSessionTests(unittest.TestCase):
  def test_resolving_a_scene_consumes_one_turn_and_records_deltas(self):
    session = create_game_session(seed=3)
    filler = item_by_kind(session, "filler")

    session.select_inbox_item(filler.id)
    result = session.resolve_current(0)

    self.assertEqual(result.turn, 1)
    self.assertEqual(session.turn, 2)
    self.assertTrue(result.changes)
    self.assertEqual(len(session.history), 1)

  def test_arc_setup_locks_actors_and_stays_in_inbox(self):
    session = create_game_session(seed=3)
    new_arc = next(
      item for item in session.available_actions()
      if item.id == "henderson"
    )

    scene = session.select_inbox_item(new_arc.id)
    self.assertFalse(scene.requires_decision)
    self.assertEqual(len(session.active_arcs), 1)
    self.assertTrue(any(npc.is_locked for npc in session.npcs))

    session.resolve_current()

    active = [
      item for item in session.available_actions()
      if item.id == "henderson"
    ]
    self.assertEqual(active[0].kind, "active_arc")

  def test_two_active_arcs_hide_new_arc_starts(self):
    session = create_game_session(seed=3)

    session.select_inbox_item("henderson")
    session.resolve_current()
    session.select_inbox_item("mentorship")
    session.resolve_current()

    self.assertEqual(len(session.active_arcs), 2)
    self.assertFalse(any(
      item.kind == "new_arc"
      for item in session.available_actions()
    ))

  def test_fillers_do_not_repeat_on_the_next_turn(self):
    session = create_game_session(seed=11)
    filler = item_by_kind(session, "filler")

    session.select_inbox_item(filler.id)
    session.resolve_current(0)

    next_filler_ids = {
      item.id for item in session.available_actions()
      if item.kind == "filler"
    }
    self.assertNotIn(filler.id, next_filler_ids)

  def test_successful_promotion_arc_promotes_once(self):
    session = create_game_session(seed=3)
    session.turn = 6
    session.player.reputation.set_value(0.4)
    session.player.political_capital.set_value(0.1)

    self.assertIn(
      "promotion",
      {item.id for item in session.available_actions()},
    )

    session.select_inbox_item("promotion")
    session.resolve_current()
    session.select_inbox_item("promotion")
    session.resolve_current(0)
    session.select_inbox_item("promotion")
    session.resolve_current(0)
    session.select_inbox_item("promotion")
    result = session.resolve_current()

    self.assertEqual(result.promoted_to, "Associate")
    self.assertEqual(session.player.role.value, "Associate")
    self.assertNotIn(
      "promotion",
      {item.id for item in session.available_actions()},
    )

  def test_failed_promotion_arc_does_not_change_role(self):
    session = create_game_session(seed=3)
    session.turn = 6
    session.player.reputation.set_value(0.4)
    session.player.political_capital.set_value(0.1)

    session.select_inbox_item("promotion")
    session.resolve_current()
    session.select_inbox_item("promotion")
    session.resolve_current(0)
    session.select_inbox_item("promotion")
    session.resolve_current(1)
    session.select_inbox_item("promotion")
    result = session.resolve_current()

    self.assertIsNone(result.promoted_to)
    self.assertEqual(session.player.role.value, "Intern")

  def test_invalid_decision_is_rejected_without_consuming_turn(self):
    session = create_game_session(seed=3)
    filler = item_by_kind(session, "filler")
    session.select_inbox_item(filler.id)

    with self.assertRaises(ValueError):
      session.resolve_current(9)

    self.assertEqual(session.turn, 1)
    self.assertIsNotNone(session.selected_scene)

  def test_campaign_ends_after_configured_turn_count(self):
    session = create_game_session(seed=3, max_turns=1)
    filler = item_by_kind(session, "filler")
    session.select_inbox_item(filler.id)
    session.resolve_current(0)

    self.assertTrue(session.is_over)
    self.assertEqual(session.available_actions(), ())


if __name__ == "__main__":
  unittest.main()
