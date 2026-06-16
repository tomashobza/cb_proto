import enum

from stats import Stat
from tags import TagEnum
from npc import ArchetypesEnum, NPC
from decision import Decision, Scenario

class Player():
  def __init__(self, name):
    self.name = name
    self.reputation = Stat("Reputation", 0)
    self.political_capital = Stat("Political Capital", 0)
    self.stress = Stat("Stress", 0)
  
  def set_stat(self, stat_name, value):
    if stat_name == "Reputation":
      self.reputation.set_value(value)
    elif stat_name == "Political Capital":
      self.political_capital.set_value(value)
    elif stat_name == "Stress":
      self.stress.set_value(value)
    else:
      raise ValueError("Invalid stat name")
  
  def get_stats(self):
    return {
      "Reputation": self.reputation.get_value(),
      "Political Capital": self.political_capital.get_value(),
      "Stress": self.stress.get_value()
    }

  def __str__(self):
    return f"{self.reputation}\n{self.political_capital}\n{self.stress}"
  
## DEV ##

if __name__ == "__main__":
  player = Player("Player")
  npc = NPC("Joe", ArchetypesEnum.LadderClimber)
  
  scenario = Scenario(
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
  player_decision = scenario.decisions[0]
  tags = player_decision.get_tags()
  npc.affect_by_tags(tags)
  print()
  print(npc)