import enum
from archetypes import ArchetypesEnum

class TagEnum(enum.Enum):
  HELPFUL = "helpful"
  AMBITIOUS = "ambitious"
  HONEST = "honest"
  POLITICAL = "political"
  BOUNDARY = "boundary"
  LOYAL = "loyal"
  CONFRONTATIONAL = "confrontational"
  CREDIT_TAKING = "credit-taking"
  TEAM_FIRST = "team-first"
  BOSS_PLEASING = "boss-pleasing"


NPC_AFFECT_BY_TAGS = {
  ArchetypesEnum.LadderClimber: {
    TagEnum.HELPFUL:        {"Warmth": 0.0,  "Respect": 0.1  },
    TagEnum.AMBITIOUS:      {"Warmth": 0.1,  "Respect": 0.3  },
    TagEnum.HONEST:         {"Warmth": 0.0,  "Respect": 0.0  },
    TagEnum.POLITICAL:      {"Warmth": 0.2,  "Respect": 0.2  },
    TagEnum.BOUNDARY:       {"Warmth": -0.1, "Respect": 0.1  },
    TagEnum.LOYAL:          {"Warmth": 0.3,  "Respect": 0.1  },
    TagEnum.CONFRONTATIONAL:{"Warmth": -0.3, "Respect": -0.1 },
    TagEnum.CREDIT_TAKING:  {"Warmth": -0.2, "Respect": 0.1  },
    TagEnum.TEAM_FIRST:     {"Warmth": 0.1,  "Respect": 0.0  },
    TagEnum.BOSS_PLEASING:  {"Warmth": 0.2,  "Respect": 0.1  }
  },
  ArchetypesEnum.Mentor: {
    TagEnum.HELPFUL:        {"Warmth": 0.2,  "Respect": 0.2  },
    TagEnum.AMBITIOUS:      {"Warmth": 0.1,  "Respect": 0.2  },
    TagEnum.HONEST:         {"Warmth": 0.3,  "Respect": 0.3  },
    TagEnum.POLITICAL:      {"Warmth": -0.2, "Respect": -0.1 },
    TagEnum.BOUNDARY:       {"Warmth": 0.1,  "Respect": 0.2  },
    TagEnum.LOYAL:          {"Warmth": 0.2,  "Respect": 0.1  },
    TagEnum.CONFRONTATIONAL:{"Warmth": -0.1, "Respect": 0.1  },
    TagEnum.CREDIT_TAKING:  {"Warmth": -0.3, "Respect": -0.2 },
    TagEnum.TEAM_FIRST:     {"Warmth": 0.3,  "Respect": 0.2  },
    TagEnum.BOSS_PLEASING:  {"Warmth": -0.1, "Respect": -0.2 }
  },
  ArchetypesEnum.Bureaucrat: {
    TagEnum.HELPFUL:        {"Warmth": 0.1,  "Respect": 0.1  },
    TagEnum.AMBITIOUS:      {"Warmth": -0.2, "Respect": -0.2 },
    TagEnum.HONEST:         {"Warmth": 0.1,  "Respect": 0.1  },
    TagEnum.POLITICAL:      {"Warmth": 0.0,  "Respect": 0.0  },
    TagEnum.BOUNDARY:       {"Warmth": 0.0,  "Respect": 0.1  },
    TagEnum.LOYAL:          {"Warmth": 0.2,  "Respect": 0.3  },
    TagEnum.CONFRONTATIONAL:{"Warmth": -0.3, "Respect": -0.3 },
    TagEnum.CREDIT_TAKING:  {"Warmth": -0.1, "Respect": -0.2 },
    TagEnum.TEAM_FIRST:     {"Warmth": 0.2,  "Respect": 0.2  },
    TagEnum.BOSS_PLEASING:  {"Warmth": 0.3,  "Respect": 0.2  }
  },
  ArchetypesEnum.Saboteur: {
    TagEnum.HELPFUL:        {"Warmth": 0.2,  "Respect": -0.1 },
    TagEnum.AMBITIOUS:      {"Warmth": -0.1, "Respect": 0.1  },
    TagEnum.HONEST:         {"Warmth": 0.1,  "Respect": 0.0  },
    TagEnum.POLITICAL:      {"Warmth": 0.1,  "Respect": 0.1  },
    TagEnum.BOUNDARY:       {"Warmth": -0.1, "Respect": 0.0  },
    TagEnum.LOYAL:          {"Warmth": 0.2,  "Respect": -0.1 },
    TagEnum.CONFRONTATIONAL:{"Warmth": -0.2, "Respect": 0.2  },
    TagEnum.CREDIT_TAKING:  {"Warmth": -0.3, "Respect": 0.0  },
    TagEnum.TEAM_FIRST:     {"Warmth": 0.2,  "Respect": -0.1 },
    TagEnum.BOSS_PLEASING:  {"Warmth": 0.1,  "Respect": -0.1 }
  },
  ArchetypesEnum.Burnout: {
    TagEnum.HELPFUL:        {"Warmth": 0.1,  "Respect": 0.0  },
    TagEnum.AMBITIOUS:      {"Warmth": -0.1, "Respect": 0.0  },
    TagEnum.HONEST:         {"Warmth": 0.1,  "Respect": 0.1  },
    TagEnum.POLITICAL:      {"Warmth": -0.1, "Respect": 0.0  },
    TagEnum.BOUNDARY:       {"Warmth": 0.3,  "Respect": 0.2  },
    TagEnum.LOYAL:          {"Warmth": 0.1,  "Respect": 0.0  },
    TagEnum.CONFRONTATIONAL:{"Warmth": 0.0,  "Respect": 0.1  },
    TagEnum.CREDIT_TAKING:  {"Warmth": -0.1, "Respect": 0.0  },
    TagEnum.TEAM_FIRST:     {"Warmth": 0.1,  "Respect": 0.0  },
    TagEnum.BOSS_PLEASING:  {"Warmth": -0.2, "Respect": -0.1 }
  }
}

PLAYER_AFFECT_BY_TAGS = {
  TagEnum.HELPFUL:        {"Reputation": 0.1,  "PoliticalCapital": 0.0,  "Stress": -0.1 },
  TagEnum.AMBITIOUS:      {"Reputation": 0.1,  "PoliticalCapital": 0.2,  "Stress": 0.1  },
  TagEnum.HONEST:         {"Reputation": 0.2,  "PoliticalCapital": -0.1, "Stress": -0.1 },
  TagEnum.POLITICAL:      {"Reputation": 0.0,  "PoliticalCapital": 0.3,  "Stress": 0.1  },
  TagEnum.BOUNDARY:       {"Reputation": 0.0,  "PoliticalCapital": -0.1, "Stress": -0.2 },
  TagEnum.LOYAL:          {"Reputation": 0.1,  "PoliticalCapital": 0.2,  "Stress": 0.0  },
  TagEnum.CONFRONTATIONAL:{"Reputation": -0.2, "PoliticalCapital": -0.1, "Stress": 0.2  },
  TagEnum.CREDIT_TAKING:  {"Reputation": 0.2,  "PoliticalCapital": 0.1,  "Stress": 0.1  },
  TagEnum.TEAM_FIRST:     {"Reputation": 0.2,  "PoliticalCapital": 0.0,  "Stress": -0.1 },
  TagEnum.BOSS_PLEASING:  {"Reputation": 0.1,  "PoliticalCapital": 0.1,  "Stress": 0.0  }
}