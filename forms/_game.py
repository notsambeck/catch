from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables
from AddContacts import AddContacts

class _game (_gameTemplate):
  def __init__(self, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.content_panel.add_component(AddContacts())    