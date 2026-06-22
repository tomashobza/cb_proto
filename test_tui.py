import unittest

from content import create_game_session
from tui import (
  CorporatePoliticsApp,
  MainScreen,
  NameScreen,
  ResultScreen,
  SceneScreen,
  SummaryScreen,
)
from textual.widgets import Input, OptionList, TabbedContent


class TUITests(unittest.IsolatedAsyncioTestCase):
  async def test_name_entry_opens_dashboard_with_status_views(self):
    app = CorporatePoliticsApp()

    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      self.assertIsInstance(app.screen, NameScreen)

      name_input = app.screen.query_one("#name-input", Input)
      name_input.value = "Ada"
      await pilot.press("enter")
      await pilot.pause()

      self.assertIsInstance(app.screen, MainScreen)
      self.assertEqual(app.screen.session.player.name, "Ada")
      self.assertGreater(
        app.screen.query_one("#inbox-list", OptionList).option_count,
        0,
      )

      await pilot.press("c")
      await pilot.pause()
      self.assertEqual(
        app.screen.query_one(TabbedContent).active,
        "coworkers-tab",
      )

  async def test_inbox_scene_and_result_flow(self):
    app = CorporatePoliticsApp()

    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      await pilot.press("enter")
      await pilot.pause()

      dashboard = app.screen
      inbox = dashboard.query_one("#inbox-list", OptionList)
      inbox.focus()
      inbox.highlighted = 0
      await pilot.press("enter")
      await pilot.pause()

      self.assertIsInstance(app.screen, SceneScreen)
      await pilot.press("enter")
      await pilot.pause()

      self.assertIsInstance(app.screen, ResultScreen)
      await pilot.press("enter")
      await pilot.pause()

      self.assertIsInstance(app.screen, MainScreen)
      self.assertEqual(app.screen.session.turn, 2)

  async def test_one_turn_campaign_reaches_summary(self):
    def short_session(name):
      return create_game_session(name, max_turns=1)

    app = CorporatePoliticsApp(session_factory=short_session)

    async with app.run_test(size=(120, 40)) as pilot:
      await pilot.pause()
      await pilot.press("enter")
      await pilot.pause()

      dashboard = app.screen
      filler = next(
        item for item in dashboard.session.available_actions()
        if item.kind == "filler"
      )
      scene = dashboard.session.select_inbox_item(filler.id)
      app.push_screen(SceneScreen(dashboard.session, scene))
      await pilot.pause()
      await pilot.press("1")
      await pilot.pause()
      self.assertIsInstance(app.screen, ResultScreen)

      await pilot.press("enter")
      await pilot.pause()
      self.assertIsInstance(app.screen, SummaryScreen)


if __name__ == "__main__":
  unittest.main()
