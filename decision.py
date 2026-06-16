from tags import TagEnum

class Decision():
  def __init__(self, description, tags: list[TagEnum]):
    self.description = description
    self.tags = tags
    
  def get_tags(self):
    return self.tags
  
  def __str__(self):
    return f"{self.description}\nTags: {', '.join([tag.value for tag in self.tags])}"
class Scenario():
  def __init__(self, description, decisions: tuple[Decision, Decision, Decision, Decision]):
    self.description = description
    self.decisions = decisions
  
  def __str__(self):
    return f"{self.description}\n\n1. {self.decisions[0]}\n2. {self.decisions[1]}\n3. {self.decisions[2]}\n4. {self.decisions[3]}"