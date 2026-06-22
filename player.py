from stats import Stat
from tags import TagEnum, PLAYER_AFFECT_BY_TAGS
from org_chart import OrgRole, next_role, normalize_role, role_level

class Player():
  def __init__(self, name, role=OrgRole.INTERN):
    self.name = name
    self.role = normalize_role(role)
    self.reputation = Stat("Reputation", 0)
    self.political_capital = Stat("Political Capital", 0)
    self.stress = Stat("Stress", 0)

  @property
  def level(self):
    return role_level(self.role)

  def set_role(self, role):
    self.role = normalize_role(role)

  def promote(self):
    promoted_role = next_role(self.role)
    if promoted_role is None:
      raise ValueError("Player is already at the top of the org chart")
    self.role = promoted_role
    return self.role
  
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
      "Role": self.role.value,
      "Level": self.level,
      "Reputation": self.reputation.get_value(),
      "Political Capital": self.political_capital.get_value(),
      "Stress": self.stress.get_value()
    }
  
  def affect_by_tags(self, tags: list[TagEnum]):
    affects = [self.affect_by_tag(tag) for tag in tags]
    return {
      "reputation": sum(affect[0] for affect in affects),
      "political_capital": sum(affect[1] for affect in affects),
      "stress": sum(affect[2] for affect in affects),
    }
  
  def affect_by_tag(self, tag: TagEnum):
    # affect NPC stats
    if tag in PLAYER_AFFECT_BY_TAGS:
      affect = PLAYER_AFFECT_BY_TAGS[tag]
      reputation_delta = affect["Reputation"]
      political_capital_delta = affect["PoliticalCapital"]
      stress_delta = affect["Stress"]
      self.reputation.update_value(reputation_delta)
      self.political_capital.update_value(political_capital_delta)
      self.stress.update_value(stress_delta)
      
      return reputation_delta, political_capital_delta, stress_delta
    
    else:
      raise ValueError(f"Tag {tag} not found in PLAYER affect mapping")


  def __str__(self):
    return f"Role: {self.role.value}\n{self.reputation}\n{self.political_capital}\n{self.stress}"
