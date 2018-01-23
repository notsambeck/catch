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
    self.game_list = []
    self.update_connections()
    
  def update_connections(self):
    server = anvil.server.call_s('get_games')
    
    if not server['success']:
      print server['msg']
      return None
    
    elif not server['order']:
      self.game_panel.clear()
      self.game_panel.add_component(Label(text='You have not added any connections yet.'))
      
    elif not self.game_list:
      self.game_panel.clear()
      self.games = server['games']
      self.game_list = server['order']
      for game in self.game_list:
        self.game_panel.add_component(GameListElement(server['games'][game]))
    
    else:
      # successfully got games from server + there are already games
      
      if server['order'] == self.game_list:
        for i, _id in enumerate(self.game_list):
          server_game = server['games'][_id]
          local_game = self.games[_id]
          if server_game['throws'] != local_game['throws']:
            self.game_panel.get_components()[i].update(server_game)
      # dumb way to repopulate for changed game list
      else:
        self.game_panel.clear()
        self.games = server['games']
        self.game_list = server['order']
        for _id in self.game_list:
          self.game_panel.add_component(GameListElement(self.games[_id]))

  def timer_1_tick(self, **event_args):
    # This method is called Every [interval] seconds
    self.update_connections()
