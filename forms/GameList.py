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
  just a list of games (each of which is an instance of GameListElement)
  
  (see AddContacts for context)
  '''
  def __init__(self, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.games = None
    self.update_connections()
    
  def add_connection(self, new_conn):
   self.game_panel.add_component(GameListElement(new_conn))
    
  def update_connections(self):
    listed = self.game_panel.get_components()
    server = anvil.server.call_s('get_games')
    
    if not server['success']:
      print server['msg']
      return None
      
    elif not listed:
      for game in server['games'].values():
        self.game_panel.add_component(GameListElement(game))
    
    else:
      # successfully got games from server + there are already games
      
      # there's no way to delete games so this is safe.
      if len(server['games']) == len(listed):
        for element in listed:
          _id = element.game.get_id()
          game = server['games'][_id]
          if game['throws'] != element.game['throws']:
            element.update(game)
      # dumb way to repopulate for additional games
      else:
        self.game_panel.clear()
        for game in server['games'].values():
          self.game_panel.add_component(GameListElement(game))

  def timer_1_tick(self, **event_args):
    # This method is called Every [interval] seconds
    self.games = self.update_connections()
