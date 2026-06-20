import random

from arc import ActorQuery, Arc, PlayerCondition
from archetypes import ArchetypesEnum
from decision import Decision
from npc import NPC
from player import Player
from scenario import Scenario
from tags import TagEnum


def main():
  player = Player("Player")
  sarah = NPC("Sarah", ArchetypesEnum.LadderClimber)
  marcus = NPC("Marcus", ArchetypesEnum.Bureaucrat)

  filler = Scenario(
    "A colleague asks whether you can review their slide deck before lunch.",
    (
      Decision("Review it now.", [TagEnum.HELPFUL], return_data={"helped": True}),
      Decision("Offer comments after lunch.", [TagEnum.BOUNDARY]),
      Decision("Ask your manager whether this is a priority.", [TagEnum.POLITICAL]),
      Decision("Suggest they ask the whole team.", [TagEnum.TEAM_FIRST]),
    ),
  )
  print("FILLER")
  print(filler)
  print("Payload:", filler.play(player, [sarah], 0))

  setup = Scenario(
    "Marcus announces that Sarah will present work you largely produced.",
    actor_roles=("manager", "rival"),
  )
  dilemma = Scenario(
    "How do you respond?",
    (
      Decision(
        "Claim the work publicly.",
        [TagEnum.AMBITIOUS, TagEnum.CREDIT_TAKING],
        return_data={"response": "public"},
      ),
      Decision(
        "Clarify your contribution privately.",
        [TagEnum.POLITICAL, TagEnum.AMBITIOUS],
        return_data={"response": "private"},
      ),
      Decision(
        "Support the presentation.",
        [TagEnum.BOSS_PLEASING, TagEnum.TEAM_FIRST],
        return_data={"response": "support"},
      ),
      Decision(
        "Let it go.",
        [TagEnum.BOUNDARY, TagEnum.HONEST],
        return_data={"response": "quiet"},
      ),
    ),
    actor_roles=("manager", "rival"),
  )
  public_aftermath = Scenario(
    "The all-hands becomes an exquisitely awkward debate about attribution.",
    actor_roles=("manager", "rival"),
  )
  quiet_aftermath = Scenario(
    "The presentation proceeds smoothly. The authorship remains strategically vague.",
    actor_roles=("manager", "rival"),
  )

  def branch_on_response(state, payload):
    del state
    return (
      "public_aftermath"
      if payload["response"] == "public"
      else "quiet_aftermath"
    )

  arc = Arc(
    "The Henderson Proposal",
    scenarios={
      "setup": setup,
      "dilemma": dilemma,
      "public_aftermath": public_aftermath,
      "quiet_aftermath": quiet_aftermath,
    },
    start_scenario_id="setup",
    actor_queries={
      "manager": ActorQuery(archetypes={ArchetypesEnum.Bureaucrat}),
      "rival": ActorQuery(archetypes={ArchetypesEnum.LadderClimber}),
    },
    conditions=(PlayerCondition("reputation", ">=", 0),),
    transitions={
      "setup": "dilemma",
      "dilemma": branch_on_response,
    },
  )

  print("\nARC")
  arc.start(player, [sarah, marcus], rng=random.Random(7))
  print(arc.current_scenario)
  arc.advance()
  print(arc.current_scenario)
  arc.choose(0)
  print(arc.current_scenario)
  arc.advance()
  print("Completed:", arc.completed)


if __name__ == "__main__":
  main()
