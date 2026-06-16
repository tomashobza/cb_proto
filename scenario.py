from decision import Decision

class Scenario():
  def __init__(self, player, actors, description, decisions: tuple[Decision, Decision, Decision, Decision]):
    self.player = player
    self.actors = actors
    self.description = description
    self.decisions = decisions
  
  def __str__(self):
    return f"{self.description}\n\n1. {self.decisions[0]}\n2. {self.decisions[1]}\n3. {self.decisions[2]}\n4. {self.decisions[3]}"
  
  def make_decision(self, decision_index):
    if decision_index < 0 or decision_index > 3:
      raise ValueError("Decision index must be between 0 and 3")
    
    decision = self.decisions[decision_index]
    tags = decision.get_tags()
    
    # affect NPCs based on decision tags
    for actor in self.actors:
      actor.affect_by_tags(tags)
    
    # affect player based on decision tags
    self.player.affect_by_tags(tags)