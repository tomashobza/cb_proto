from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import (
  Button,
  DataTable,
  Footer,
  Header,
  Input,
  Label,
  OptionList,
  Static,
  TabbedContent,
  TabPane,
)
from textual.widgets.option_list import Option

from content import create_game_session


def _bar(value, width=18):
  filled = round(((value + 1) / 2) * width)
  filled = max(0, min(width, filled))
  return f"[{'█' * filled}{'·' * (width - filled)}] {value:+.1f}"


class NameScreen(Screen):
  CSS = """
  NameScreen {
    align: center middle;
    background: $background;
  }
  #name-card {
    width: 64;
    height: auto;
    border: round $accent;
    padding: 2 4;
    background: $surface;
  }
  #title {
    text-style: bold;
    color: $accent;
    text-align: center;
    margin-bottom: 1;
  }
  #name-input {
    margin: 1 0;
  }
  #start-button {
    width: 100%;
  }
  """

  def compose(self) -> ComposeResult:
    with Vertical(id="name-card"):
      yield Label("CIRCLE BACK", id="title")
      yield Static(
        "A corporate politics learning simulator.\n"
        "Your contribution has been noticed and will be discussed offline."
      )
      yield Input(placeholder="Your name (default: Alex)", id="name-input")
      yield Button("Begin Internship", id="start-button", variant="primary")

  def on_mount(self):
    self.query_one("#name-input", Input).focus()

  def on_input_submitted(self, event: Input.Submitted):
    self._start(event.value)

  def on_button_pressed(self, event: Button.Pressed):
    if event.button.id == "start-button":
      self._start(self.query_one("#name-input", Input).value)

  def _start(self, name):
    self.app.start_campaign(name.strip() or "Alex")


class MainScreen(Screen):
  BINDINGS = [
    ("q", "quit", "Quit"),
    ("i", "tab('inbox-tab')", "Inbox"),
    ("c", "tab('coworkers-tab')", "Coworkers"),
    ("a", "tab('arcs-tab')", "Arcs"),
    ("h", "tab('history-tab')", "History"),
  ]

  CSS = """
  MainScreen {
    layout: vertical;
  }
  #campaign-status {
    height: 3;
    padding: 0 2;
    background: $primary-background;
    color: $text;
    text-style: bold;
    content-align: left middle;
  }
  #player-stats {
    height: 5;
    padding: 1 2;
    border-bottom: solid $accent;
  }
  TabbedContent {
    height: 1fr;
  }
  TabPane {
    padding: 1;
  }
  #inbox-help {
    height: 2;
    color: $text-muted;
  }
  #inbox-list {
    height: 1fr;
    border: round $accent;
  }
  DataTable {
    height: 1fr;
  }
  .empty-message {
    color: $text-muted;
    padding: 1;
  }
  """

  def __init__(self, session):
    super().__init__()
    self.session = session

  def compose(self) -> ComposeResult:
    yield Header(show_clock=True)
    yield Static(id="campaign-status")
    yield Static(id="player-stats")
    with TabbedContent(initial="inbox-tab"):
      with TabPane("Inbox", id="inbox-tab"):
        yield Static("Select the next item to address. One scene consumes one turn.", id="inbox-help")
        yield OptionList(id="inbox-list")
      with TabPane("Coworkers", id="coworkers-tab"):
        yield DataTable(id="coworker-table", zebra_stripes=True)
      with TabPane("Active Arcs", id="arcs-tab"):
        yield VerticalScroll(Static(id="arcs-content"))
      with TabPane("History", id="history-tab"):
        yield VerticalScroll(Static(id="history-content"))
    yield Footer()

  def on_mount(self):
    table = self.query_one("#coworker-table", DataTable)
    table.add_columns("Name", "Role", "Archetype", "Warmth", "Respect", "Status")
    table.cursor_type = "row"
    self.refresh_view()

  def refresh_view(self):
    player = self.session.player
    self.query_one("#campaign-status", Static).update(
      f"Turn {min(self.session.turn, self.session.max_turns)}/{self.session.max_turns}"
      f"  •  {player.name}, {player.role.value}"
      f"  •  Active arcs {len(self.session.active_arcs)}/{self.session.max_active_arcs}"
    )
    self.query_one("#player-stats", Static).update(
      "REPUTATION       "
      f"{_bar(player.reputation.get_value())}\n"
      "POLITICAL CAPITAL "
      f"{_bar(player.political_capital.get_value())}\n"
      "STRESS            "
      f"{_bar(player.stress.get_value())}"
    )

    inbox = self.query_one("#inbox-list", OptionList)
    inbox.clear_options()
    inbox.add_options([
      Option(
        f"[b]{item.title}[/b]  [dim]{item.kind.replace('_', ' ')}[/dim]\n"
        f"{item.summary}",
        id=item.id,
      )
      for item in self.session.available_actions()
    ])

    table = self.query_one("#coworker-table", DataTable)
    table.clear(columns=False)
    for npc in sorted(self.session.npcs, key=lambda coworker: (-coworker.level, coworker.name)):
      table.add_row(
        npc.name,
        npc.role.value,
        npc.archetype.value,
        f"{npc.warmth.get_value():+.1f}",
        f"{npc.respect.get_value():+.1f}",
        "In active arc" if npc.is_locked else "Available",
      )

    active_lines = []
    for campaign_arc in self.session.active_arcs:
      actors = ", ".join(
        f"{role}: {npc.name}"
        for role, npc in campaign_arc.arc.actors.items()
      )
      active_lines.append(
        f"[b]{campaign_arc.arc.name}[/b]\n"
        f"Next: {campaign_arc.arc.current_scenario.description}\n"
        f"Cast: {actors}"
      )
    self.query_one("#arcs-content", Static).update(
      "\n\n".join(active_lines)
      if active_lines
      else "[dim]No active arcs. Enjoy this brief and suspicious calm.[/dim]"
    )

    history_lines = [
      f"[b]Turn {result.turn}: {result.title}[/b]\n"
      f"{result.choice or 'Continued'}"
      for result in reversed(self.session.history)
    ]
    self.query_one("#history-content", Static).update(
      "\n\n".join(history_lines)
      if history_lines
      else "[dim]No documented decisions yet.[/dim]"
    )

  def on_option_list_option_selected(self, event: OptionList.OptionSelected):
    scene = self.session.select_inbox_item(event.option.id)
    self.app.push_screen(SceneScreen(self.session, scene))

  def action_tab(self, tab_id):
    self.query_one(TabbedContent).active = tab_id


class SceneScreen(Screen):
  BINDINGS = [
    ("q", "quit", "Quit"),
    ("1", "choose(0)", "Choice 1"),
    ("2", "choose(1)", "Choice 2"),
    ("3", "choose(2)", "Choice 3"),
    ("4", "choose(3)", "Choice 4"),
    ("enter", "continue_scene", "Continue"),
  ]

  CSS = """
  SceneScreen {
    align: center middle;
    background: $background 90%;
  }
  #scene-card {
    width: 90%;
    max-width: 100;
    height: auto;
    max-height: 90%;
    border: round $accent;
    padding: 1 2;
    background: $surface;
  }
  #scene-title {
    text-style: bold;
    color: $accent;
    margin-bottom: 1;
  }
  #scene-description {
    margin-bottom: 1;
  }
  #scene-actors {
    color: $text-muted;
    margin-bottom: 1;
  }
  .decision {
    width: 100%;
    height: auto;
    min-height: 3;
    margin: 0 0 1 0;
  }
  #continue-button {
    width: 100%;
  }
  """

  def __init__(self, session, scene):
    super().__init__()
    self.session = session
    self.scene = scene

  def compose(self) -> ComposeResult:
    with VerticalScroll(id="scene-card"):
      yield Static(self.scene.title, id="scene-title")
      yield Static(self.scene.description, id="scene-description")
      actor_text = " • ".join(
        f"{role}: {name}" for role, name in self.scene.actors
      )
      yield Static(actor_text or "No named actors", id="scene-actors")
      if self.scene.requires_decision:
        for decision in self.scene.decisions:
          tags = ", ".join(decision.tags)
          yield Button(
            f"{decision.index + 1}. {decision.description}\n[{tags}]",
            id=f"choice-{decision.index}",
            classes="decision",
          )
      else:
        yield Button("Continue", id="continue-button", variant="primary")
    yield Footer()

  def on_mount(self):
    target = "#choice-0" if self.scene.requires_decision else "#continue-button"
    self.query_one(target, Button).focus()

  def on_button_pressed(self, event: Button.Pressed):
    if event.button.id == "continue-button":
      self._resolve()
    elif event.button.id and event.button.id.startswith("choice-"):
      self._resolve(int(event.button.id.split("-")[1]))

  def action_choose(self, index):
    if self.scene.requires_decision:
      self._resolve(index)

  def action_continue_scene(self):
    if not self.scene.requires_decision:
      self._resolve()

  def _resolve(self, decision_index=None):
    result = self.session.resolve_current(decision_index)
    self.app.switch_screen(ResultScreen(self.session, result))


class ResultScreen(Screen):
  BINDINGS = [
    ("q", "quit", "Quit"),
    ("enter", "continue_game", "Continue"),
  ]

  CSS = """
  ResultScreen {
    align: center middle;
    background: $background 90%;
  }
  #result-card {
    width: 76;
    height: auto;
    max-height: 90%;
    border: round $success;
    padding: 1 3;
    background: $surface;
  }
  #result-title {
    text-style: bold;
    color: $success;
    margin-bottom: 1;
  }
  #result-continue {
    width: 100%;
    margin-top: 1;
  }
  """

  def __init__(self, session, result):
    super().__init__()
    self.session = session
    self.result = result

  def compose(self) -> ComposeResult:
    with VerticalScroll(id="result-card"):
      yield Static(f"Turn {self.result.turn} resolved", id="result-title")
      yield Static(self._result_text(), id="result-text")
      yield Button("Continue", id="result-continue", variant="success")
    yield Footer()

  def on_mount(self):
    self.query_one("#result-continue", Button).focus()

  def on_button_pressed(self, event: Button.Pressed):
    if event.button.id == "result-continue":
      self.action_continue_game()

  def action_continue_game(self):
    if self.session.is_over:
      self.app.switch_screen(SummaryScreen(self.session))
    else:
      self.app.return_to_dashboard()

  def _result_text(self):
    lines = [f"[b]{self.result.title}[/b]"]
    if self.result.choice:
      lines.append(f"Decision: {self.result.choice}")
    if self.result.changes:
      lines.append("")
      lines.append("[b]Observed effects[/b]")
      for change in self.result.changes:
        color = "green" if change.delta > 0 else "red"
        lines.append(
          f"{change.subject} — {change.stat}: "
          f"[{color}]{change.delta:+.1f}[/{color}] "
          f"({change.before:+.1f} → {change.after:+.1f})"
        )
    else:
      lines.append("\nNo measurable relationship changes. The meeting was still mandatory.")
    if self.result.arc_completed:
      lines.append(f"\nArc completed: [b]{self.result.arc_completed}[/b]")
    if self.result.promoted_to:
      lines.append(f"[bold green]Promotion secured: {self.result.promoted_to}[/bold green]")
    return "\n".join(lines)


class SummaryScreen(Screen):
  BINDINGS = [
    ("q", "quit", "Quit"),
  ]

  CSS = """
  SummaryScreen {
    align: center middle;
  }
  #summary-card {
    width: 86;
    height: auto;
    max-height: 92%;
    border: double $accent;
    padding: 1 3;
  }
  #summary-title {
    text-style: bold;
    color: $accent;
    text-align: center;
    margin-bottom: 1;
  }
  #quit-button {
    width: 100%;
    margin-top: 1;
  }
  """

  def __init__(self, session):
    super().__init__()
    self.session = session

  def compose(self) -> ComposeResult:
    with VerticalScroll(id="summary-card"):
      yield Static("FINAL PERFORMANCE CALIBRATION", id="summary-title")
      yield Static(self._summary_text(), id="summary-text")
      yield Button("Exit", id="quit-button", variant="primary")
    yield Footer()

  def on_mount(self):
    self.query_one("#quit-button", Button).focus()

  def on_button_pressed(self, event: Button.Pressed):
    if event.button.id == "quit-button":
      self.app.exit()

  def _summary_text(self):
    player = self.session.player
    completed = ", ".join(
      arc.arc.name for arc in self.session.completed_arcs
    ) or "None"
    relationships = "\n".join(
      f"{npc.name} ({npc.role.value}, {npc.archetype.value}): "
      f"warmth {npc.warmth.get_value():+.1f}, respect {npc.respect.get_value():+.1f}"
      for npc in sorted(self.session.npcs, key=lambda coworker: coworker.name)
    )
    return (
      f"[b]{player.name} — {player.role.value}[/b]\n"
      f"Reputation: {player.reputation.get_value():+.1f}\n"
      f"Political capital: {player.political_capital.get_value():+.1f}\n"
      f"Stress: {player.stress.get_value():+.1f}\n\n"
      f"Completed arcs: {completed}\n\n"
      f"[b]Coworker relationships[/b]\n{relationships}\n\n"
      f"[b]Rating: {self.session.final_rating()}[/b]"
    )


class CorporatePoliticsApp(App):
  TITLE = "Circle Back"
  SUB_TITLE = "Corporate Politics Simulator"

  CSS = """
  Screen {
    background: #10141f;
  }
  Header {
    background: #24304a;
  }
  Footer {
    background: #24304a;
  }
  """

  def __init__(self, session_factory=create_game_session):
    super().__init__()
    self.session_factory = session_factory

  def on_mount(self):
    self.push_screen(NameScreen())

  def start_campaign(self, name):
    session = self.session_factory(name)
    self.switch_screen(MainScreen(session))

  def return_to_dashboard(self):
    self.pop_screen()
    dashboard = self.screen
    if isinstance(dashboard, MainScreen):
      dashboard.refresh_view()
