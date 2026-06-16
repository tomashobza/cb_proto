from scenario import Scenario

class Arc():
  def __init__(self, name, scenarios: list[Scenario]):
    self.name = name
    self.scenarios = scenarios
    self.ad_hoc_tags = []  # list of tags that are not associated with any scenario but can affect the arc
    
    # TODO: scenario states machine - handled either via the callbacks or better yet the return data on decisions. This will allow for branching scenarios and more complex arcs (return data can be a reference to the next scenario to be played, or a function that returns the next scenario based on the current state of the arc)
    
    # TODO: implement Arc conditions - these are conditions that must be met for the arc to be available to the player. For example, a certain stat level, or a certain tag being present. This will allow for more complex arcs that can be unlocked based on player choices and stats.
    
    # TODO: implement actor selector. the scenario should be defined with a list of "query" criteria for actors, the actors inside the scenarios of the arc will be defined "canonically" and the engine will select the actors that match the criteria out of all the actors (if multiple actors match the criteria, the engine will select one at random). This will allow the arc to select NPCs not only of a certain archetype, but also with certain stats, or just the stats.