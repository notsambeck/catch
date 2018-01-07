from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables
from validators import is_valid_number
from Title import Title
from GameGrid import GameGrid


class GameList (GameListTemplate):
  def __init__(self, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.title_panel.add_component(Title())
    self.conns = self.update_connections()

  def update_connections(self):
    self.game_panel.clear()
    conns = anvil.server.call('get_connections')
    for conn in conns:
      self.game_panel.add_component(GameGrid(conn))
    return conns

  def add_contacts_click (self, **event_args):
    # This method is called when the button is clicked
    open_form('AddContacts')

      
    
 