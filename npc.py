import enum
from stats import Stat
from tags import TagEnum, NPC_AFFECT_BY_TAGS, PLAYER_AFFECT_BY_TAGS
from archetypes import ArchetypesEnum

class NPC():
  def __init__(self, name, archetype: ArchetypesEnum):
    self.name = name
    self.archetype = archetype
    self.warmth = Stat("Warmth", 0)
    self.respect = Stat("Respect", 0)
  
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
    return f"{self.name}\n{self.warmth}\n{self.respect}"