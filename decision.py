from tags import TagEnum

class Decision():
  def __init__(self, description, tags: list[TagEnum]):
    self.description = description
    self.tags = tags

  def get_tags(self):
    return self.tags

  def __str__(self):
    return f"{self.description}\nTags: {', '.join([tag.value for tag in self.tags])}"
