from anvil import *
import anvil.users
import anvil.server
import tables
from tables import app_tables


class game_list (game_listTemplate):
  def __init__(self, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.conns = anvil.server.call('get_connections')
    for thing in self.conns:
      print(thing['recipient'])
    
  def add_contacts_click (self, **event_args):
    # This method is called when the button is clicked
    open_form('add_contacts')








