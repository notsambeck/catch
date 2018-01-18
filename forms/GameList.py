from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables
from utils import is_valid_number
from Title import Title
from GameGrid import GameGrid


class GameList (GameListTemplate):
  '''
  the list of games (each of which is an instance of GameGrid)
  
  NO ADDITIONAL STUFF (see AddContacts)
  '''
  def __init__(self, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.conns = self.update_connections()
    
  def update_connections(self):
    conns = anvil.server.call('get_connections')
    self.game_panel.clear()
    for conn in conns:
      self.game_panel.add_component(GameGrid(conn))
    return conns
  
  def timer_1_tick(self, **event_args):
    # This method is called Every [interval] seconds
    self.conns = self.update_connections()
