class Stat():
  def __init__(self, name, value):
    self.name = name
    self.value = value
  
  def set_value(self, value):
    assert -1 <= value <= 1, "Value must be between -1 and 1"
    self.value = value
  
  def update_value(self, delta):
    new_value = self.value + delta
    new_value = max(-1, min(1, new_value))  # clamp value between -1 and 1
    self.set_value(new_value)
  
  def get_value(self):
    return self.value
    
  def __str__(self):
    return f"{self.name}: {self.value}"