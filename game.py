import enum

from stats import Stat
from tags import TagEnum
from npc import ArchetypesEnum, NPC
from decision import Decision
from scenario import Scenario
from player import Player

## DEV ##

if __name__ == "__main__":
  player = Player("Player")
  npc = NPC("Joe", ArchetypesEnum.LadderClimber)
  
  scenario = Scenario(
    player,
    [npc],
    "Your manager Marcus sends a message in #team-updates: \"Great work on the Henderson proposal everyone. Let's make sure we highlight this in the all-hands.\" You know this was 80% your work. Sarah (Ladder Climber) replies instantly: \"Thanks Marcus! Excited to present it together 🙌",
    (
      Decision("Reply publicly: \"Happy to take the lead on the all-hands presentation since I drove most of the analysis.\"", [TagEnum.AMBITIOUS, TagEnum.CREDIT_TAKING]),
      Decision("DM Marcus directly to clarify your contribution and offer to present.", [TagEnum.POLITICAL, TagEnum.AMBITIOUS]),
      Decision("Reply in the thread: \"Thanks Marcus! Let me know how I can help make the presentation great.\"", [TagEnum.BOSS_PLEASING, TagEnum.TEAM_FIRST]),
      Decision("Let it go. Your work speaks for itself.", [TagEnum.BOUNDARY, TagEnum.HONEST])
    )
  )
  
  print(npc)
  print()
  print(scenario)
  
  # get player's decision (for testing, we'll just choose the first one)
  scenario.make_decision(0)
  print()
  print(npc)