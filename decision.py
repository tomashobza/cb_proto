from tags import TagEnum

class Decision():
  def __init__(self, description, tags: list[TagEnum], callback=None, return_data=None):
    self.description = description
    self.tags = tags
    self.callback = callback
    self.return_data = return_data

  def get_tags(self):
    return self.tags

  def get_return_data(self):
    return self.return_data
  
  # a callback can be any function that is executed when the decision is chosen. This can be used to trigger events, update game state, etc.
  def execute_callback(self):
    if self.callback:
      self.callback()
  
  def choose(self):
    self.execute_callback()
    return self.get_tags()

  def __str__(self):
    return f"{self.description}\nTags: {', '.join([tag.value for tag in self.tags])}"
