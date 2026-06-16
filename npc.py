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
    for tag in tags:
      self.affect_by_tag(tag)
  
  def affect_by_tag(self, tag: TagEnum):
    # affect NPC stats
    if tag in NPC_AFFECT_BY_TAGS[self.archetype]:
      affect = NPC_AFFECT_BY_TAGS[self.archetype][tag]
      self.warmth.update_value(affect["Warmth"])
      self.respect.update_value(affect["Respect"])

  def __str__(self):
    return f"{self.name}\n{self.warmth}\n{self.respect}"