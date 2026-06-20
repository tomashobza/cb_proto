import enum
from stats import Stat
from tags import TagEnum, NPC_AFFECT_BY_TAGS, PLAYER_AFFECT_BY_TAGS
from archetypes import ArchetypesEnum
from org_chart import OrgRole, normalize_role, role_level

class NPC():
  def __init__(self, name, archetype: ArchetypesEnum, role=OrgRole.ASSOCIATE):
    self.name = name
    self.archetype = archetype
    self.role = normalize_role(role)
    self.warmth = Stat("Warmth", 0)
    self.respect = Stat("Respect", 0)
    self._locked_by = None

  @property
  def level(self):
    return role_level(self.role)

  @property
  def is_locked(self):
    return self._locked_by is not None

  def lock_for(self, owner):
    if self._locked_by is not None and self._locked_by is not owner:
      raise RuntimeError(f"{self.name} is already assigned to another arc")
    self._locked_by = owner

  def unlock_for(self, owner):
    if self._locked_by is owner:
      self._locked_by = None
  
  def affect_by_tags(self, tags: list[TagEnum]):
    affects = [self.affect_by_tag(tag) for tag in tags]
    sum_warmth = sum(affect[0] for affect in affects)
    sum_respect = sum(affect[1] for affect in affects)
    
    # print explaination of how player stats are affected
    print(f"{self.name} now {sum_warmth > 0 and 'warmer' or 'colder'} towards you and has {sum_respect > 0 and 'more' or 'less'} respect for you.")
  
  def affect_by_tag(self, tag: TagEnum):
    # affect NPC stats
    if tag in NPC_AFFECT_BY_TAGS[self.archetype]:
      affect = NPC_AFFECT_BY_TAGS[self.archetype][tag]
      warmth_delta = affect["Warmth"]
      respect_delta = affect["Respect"]
      self.warmth.update_value(warmth_delta)
      self.respect.update_value(respect_delta)
      
      return warmth_delta, respect_delta
    
    else:
      raise ValueError(f"Tag {tag} not found in NPC affect mapping for archetype {self.archetype}")

  def __str__(self):
    return f"{self.name}\nRole: {self.role.value}\n{self.warmth}\n{self.respect}"
