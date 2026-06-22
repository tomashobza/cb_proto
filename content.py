from arc import ActorQuery, Arc, PlayerCondition
from archetypes import ArchetypesEnum
from campaign import CampaignArc, FillerEvent, GameSession
from decision import Decision
from npc import NPC
from org_chart import OrgRole
from player import Player
from scenario import Scenario
from tags import TagEnum


def _decisions(*choices):
  return tuple(
    Decision(description, tags, return_data=payload)
    for description, tags, payload in choices
  )


def _henderson_arc():
  scenarios = {
    "setup": Scenario(
      "Marcus announces that Sarah will present work you largely produced.",
      actor_roles=("manager", "rival"),
    ),
    "dilemma": Scenario(
      "Sarah asks whether you can send her your notes before the all-hands.",
      _decisions(
        ("Send everything and wish her luck.", [TagEnum.TEAM_FIRST], {"route": "support"}),
        ("Send the notes with your name on every slide.", [TagEnum.CREDIT_TAKING], {"route": "claim"}),
        ("Ask Marcus to clarify ownership first.", [TagEnum.POLITICAL], {"route": "manager"}),
        ("Decline because you have your own deadlines.", [TagEnum.BOUNDARY], {"route": "boundary"}),
      ),
      actor_roles=("manager", "rival"),
    ),
    "escalation": Scenario(
      "At rehearsal, Sarah introduces the deck as 'a team effort' and Marcus looks relieved.",
      _decisions(
        ("Correct the record in the room.", [TagEnum.CONFRONTATIONAL, TagEnum.HONEST], None),
        ("Privately negotiate a co-presenter credit.", [TagEnum.POLITICAL, TagEnum.AMBITIOUS], None),
        ("Let Sarah present and visibly support her.", [TagEnum.LOYAL, TagEnum.TEAM_FIRST], None),
        ("Forward the original draft to leadership.", [TagEnum.CREDIT_TAKING, TagEnum.AMBITIOUS], None),
      ),
      actor_roles=("manager", "rival"),
    ),
    "aftermath": Scenario(
      "The presentation lands. Everyone agrees the collaboration was exemplary, though nobody agrees who collaborated.",
      actor_roles=("manager", "rival"),
    ),
  }
  return CampaignArc(
    "henderson",
    Arc(
      "The Henderson Proposal",
      scenarios,
      "setup",
      actor_queries={
        "manager": ActorQuery(
          archetypes={ArchetypesEnum.Bureaucrat},
          roles={OrgRole.MANAGER},
        ),
        "rival": ActorQuery(
          archetypes={ArchetypesEnum.LadderClimber},
          role_level=(OrgRole.INTERN, OrgRole.SENIOR_ASSOCIATE),
        ),
      },
      transitions={
        "setup": "dilemma",
        "dilemma": "escalation",
        "escalation": "aftermath",
      },
    ),
  )


def _mentorship_arc():
  scenarios = {
    "setup": Scenario(
      "Priya offers to mentor you. Devon immediately volunteers to 'help structure the relationship.'",
      actor_roles=("mentor", "observer"),
    ),
    "dilemma": Scenario(
      "Priya asks what you actually want from the mentorship.",
      _decisions(
        ("Give an honest account of where you are struggling.", [TagEnum.HONEST], None),
        ("Ask how to become visible to senior leadership.", [TagEnum.AMBITIOUS], None),
        ("Say you want to help the whole team improve.", [TagEnum.TEAM_FIRST], None),
        ("Ask Devon what answer would play best.", [TagEnum.POLITICAL], None),
      ),
      actor_roles=("mentor", "observer"),
    ),
    "escalation": Scenario(
      "Devon circulates a mentorship plan containing several of your ideas and none of your name.",
      _decisions(
        ("Call Devon out in front of Priya.", [TagEnum.CONFRONTATIONAL], None),
        ("Thank Devon, then calmly document your authorship.", [TagEnum.HONEST, TagEnum.CREDIT_TAKING], None),
        ("Let it go to protect the relationship.", [TagEnum.LOYAL], None),
        ("Rewrite the plan as a shared team document.", [TagEnum.TEAM_FIRST], None),
      ),
      actor_roles=("mentor", "observer"),
    ),
    "aftermath": Scenario(
      "Priya schedules another session. Devon schedules a pre-session for the session.",
      actor_roles=("mentor", "observer"),
    ),
  }
  return CampaignArc(
    "mentorship",
    Arc(
      "Mentorship, With Stakeholders",
      scenarios,
      "setup",
      actor_queries={
        "mentor": ActorQuery(archetypes={ArchetypesEnum.Mentor}),
        "observer": ActorQuery(archetypes={ArchetypesEnum.Saboteur}),
      },
      transitions={
        "setup": "dilemma",
        "dilemma": "escalation",
        "escalation": "aftermath",
      },
    ),
  )


def _capacity_arc():
  scenarios = {
    "setup": Scenario(
      "Elaine launches a capacity initiative. Jules has been nominated as capacity.",
      actor_roles=("sponsor", "burnout"),
    ),
    "dilemma": Scenario(
      "Jules asks you to cover a report that appears to have no reader.",
      _decisions(
        ("Take the report off their plate.", [TagEnum.HELPFUL], None),
        ("Ask Elaine to cancel the report.", [TagEnum.CONFRONTATIONAL], None),
        ("Offer to split it and set a firm time limit.", [TagEnum.BOUNDARY, TagEnum.TEAM_FIRST], None),
        ("Explain why completing it signals commitment.", [TagEnum.BOSS_PLEASING], None),
      ),
      actor_roles=("sponsor", "burnout"),
    ),
    "escalation": Scenario(
      "Elaine praises the initiative and adds a weekly capacity dashboard.",
      _decisions(
        ("Volunteer to own the dashboard.", [TagEnum.AMBITIOUS, TagEnum.BOSS_PLEASING], None),
        ("Suggest tracking fewer things.", [TagEnum.HONEST, TagEnum.BOUNDARY], None),
        ("Ask Jules to present the risks.", [TagEnum.TEAM_FIRST], None),
        ("Quietly automate the numbers and say nothing.", [TagEnum.HELPFUL], None),
      ),
      actor_roles=("sponsor", "burnout"),
    ),
    "aftermath": Scenario(
      "The capacity initiative produces a clear finding: everyone needs more capacity reporting.",
      actor_roles=("sponsor", "burnout"),
    ),
  }
  return CampaignArc(
    "capacity",
    Arc(
      "The Capacity Initiative",
      scenarios,
      "setup",
      actor_queries={
        "sponsor": ActorQuery(
          archetypes={ArchetypesEnum.Bureaucrat},
          role_level=(OrgRole.DIRECTOR, OrgRole.C_SUITE),
        ),
        "burnout": ActorQuery(archetypes={ArchetypesEnum.Burnout}),
      },
      transitions={
        "setup": "dilemma",
        "dilemma": "escalation",
        "escalation": "aftermath",
      },
    ),
  )


def _promotion_arc():
  def promotion_branch(state, payload):
    del state
    return "promoted" if payload.get("promotion") else "deferred"

  scenarios = {
    "setup": Scenario(
      "Marcus invites you to a meeting titled 'Quick Career Chat — No Prep Needed.'",
      actor_roles=("manager",),
    ),
    "dilemma": Scenario(
      "He asks how you think your internship is going.",
      _decisions(
        ("Describe your results directly.", [TagEnum.HONEST, TagEnum.AMBITIOUS], None),
        ("Emphasize how much the team taught you.", [TagEnum.TEAM_FIRST], None),
        ("Ask what answer the promotion committee expects.", [TagEnum.POLITICAL], None),
        ("Say titles are not important to you.", [TagEnum.BOUNDARY], None),
      ),
      actor_roles=("manager",),
    ),
    "escalation": Scenario(
      "Marcus says there may be one Associate opening, subject to a compelling business case.",
      _decisions(
        ("Make the case with concrete contributions.", [TagEnum.HONEST, TagEnum.CREDIT_TAKING], {"promotion": True}),
        ("Promise total availability next quarter.", [TagEnum.BOSS_PLEASING], {"promotion": False}),
        ("Suggest the title can wait if the work expands now.", [TagEnum.LOYAL], {"promotion": False}),
        ("Ask who else is being considered.", [TagEnum.POLITICAL, TagEnum.CONFRONTATIONAL], {"promotion": False}),
      ),
      actor_roles=("manager",),
    ),
    "promoted": Scenario(
      "You are promoted to Associate. The salary adjustment is described as 'administratively adjacent.'",
      actor_roles=("manager",),
    ),
    "deferred": Scenario(
      "Marcus says you are already operating at the next level, which is apparently why changing your level can wait.",
      actor_roles=("manager",),
    ),
  }
  return CampaignArc(
    "promotion",
    Arc(
      "A Quick Career Chat",
      scenarios,
      "setup",
      actor_queries={
        "manager": ActorQuery(
          roles={OrgRole.MANAGER},
          warmth=(0.2, 1),
          respect=(0.2, 1),
        ),
      },
      conditions=(
        PlayerCondition("reputation", ">=", 0.4),
        PlayerCondition("political_capital", ">=", 0.1),
        PlayerCondition("level", "==", OrgRole.INTERN),
      ),
      transitions={
        "setup": "dilemma",
        "dilemma": "escalation",
        "escalation": promotion_branch,
      },
    ),
    promotion=True,
    available_from_turn=6,
  )


def _fillers():
  return (
    FillerEvent(
      "deck_review",
      "Slide Deck Triage",
      Scenario(
        "Sarah asks whether you can review her slide deck before lunch.",
        _decisions(
          ("Review it now.", [TagEnum.HELPFUL], None),
          ("Offer comments after lunch.", [TagEnum.BOUNDARY], None),
          ("Ask Marcus whether it is a priority.", [TagEnum.POLITICAL], None),
          ("Suggest a team review.", [TagEnum.TEAM_FIRST], None),
        ),
      ),
      ("Sarah",),
    ),
    FillerEvent(
      "calendar",
      "Calendar Alignment",
      Scenario(
        "Devon schedules a meeting to determine whether a meeting is necessary.",
        _decisions(
          ("Accept and prepare an agenda.", [TagEnum.LOYAL], None),
          ("Decline with a written recommendation.", [TagEnum.BOUNDARY], None),
          ("Invite senior leadership.", [TagEnum.POLITICAL], None),
          ("Ask Devon to decide asynchronously.", [TagEnum.CONFRONTATIONAL], None),
        ),
      ),
      ("Devon",),
    ),
    FillerEvent(
      "lunch",
      "Strategic Lunch",
      Scenario(
        "Jules is eating lunch alone while finishing a spreadsheet.",
        _decisions(
          ("Sit down and help.", [TagEnum.HELPFUL], None),
          ("Tell them to close the laptop.", [TagEnum.BOUNDARY], None),
          ("Ask what the spreadsheet is for.", [TagEnum.HONEST], None),
          ("Mention the sacrifice to Elaine.", [TagEnum.POLITICAL], None),
        ),
      ),
      ("Jules",),
    ),
    FillerEvent(
      "process",
      "Process Improvement",
      Scenario(
        "Elaine asks for ideas to simplify a nine-step approval process.",
        _decisions(
          ("Remove six steps.", [TagEnum.CONFRONTATIONAL], None),
          ("Offer to document all nine.", [TagEnum.BOSS_PLEASING], None),
          ("Ask the team which steps matter.", [TagEnum.TEAM_FIRST], None),
          ("Volunteer to own the redesign.", [TagEnum.AMBITIOUS], None),
        ),
      ),
      ("Elaine",),
    ),
  )


def create_game_session(player_name="Alex", *, seed=7, max_turns=12):
  player = Player(player_name or "Alex")
  npcs = [
    NPC("Sarah", ArchetypesEnum.LadderClimber, OrgRole.ASSOCIATE),
    NPC("Marcus", ArchetypesEnum.Bureaucrat, OrgRole.MANAGER),
    NPC("Priya", ArchetypesEnum.Mentor, OrgRole.DIRECTOR),
    NPC("Devon", ArchetypesEnum.Saboteur, OrgRole.SENIOR_ASSOCIATE),
    NPC("Jules", ArchetypesEnum.Burnout, OrgRole.ASSOCIATE),
    NPC("Elaine", ArchetypesEnum.Bureaucrat, OrgRole.VP),
  ]
  npcs[1].warmth.set_value(0.2)
  npcs[1].respect.set_value(0.2)
  return GameSession(
    player,
    npcs,
    (
      _henderson_arc(),
      _mentorship_arc(),
      _capacity_arc(),
      _promotion_arc(),
    ),
    _fillers(),
    max_turns=max_turns,
    seed=seed,
  )
