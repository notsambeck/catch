from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables
from utils import is_valid_number
from Title import Title
from GameListElement import GameListElement


class GameList(GameListTemplate):
  '''
  the list of games (each of which is an instance of GameGrid)
  
  NO ADDITIONAL STUFF (see AddContacts)
  '''
  def __init__(self, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.conns = None
    self.conns = self.update_connections()
    
  def add_connection(self, new_conn):
   self.game_panel.add_component(GameListElement(new_conn))
    
  def update_connections(self):
    connects = anvil.server.call_s('get_games')
    if not connects['success']:
      print(connects['msg'])
      return self.conns

    if self.conns is None or connects['games'] != self.conns:
      
      self.game_panel.clear()
      for row in connects['games']:
        game = row['game']
        self.game_panel.add_component(GameListElement(game))
      return connects['games']
  
  def timer_1_tick(self, **event_args):
    # This method is called Every [interval] seconds
    self.conns = self.update_connections()
