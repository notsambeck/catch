from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables
from GameListContacts import GameListContacts
from GameListElement import GameListElement
from GameListWall import GameListWall

class _play_copy (_play_copyTemplate):
  def __init__(self, game=None, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)

    # Any code you write here will run when the form opens.

    name = anvil.users.get_user()['handle']
    self.handle.text = 'logged in as: {}'.format(name)  # menu bar
    
    self.content_panel.add_component(GameListWall())
    
    self.games = None
    self.game_list = []
    self.update_connections()
    
    self.content_panel.add_component(GameListContacts())
    
    
  def update_connections(self):
    server = anvil.server.call_s('get_games')
    
    if not server['success']:
      print server['msg']
      return None
    
    elif not server['order']:
      self.content_panel.add_component(Label(text='You have not added any connections yet.'))
      
    elif not self.game_list:
      self.games = server['games']
      self.game_list = server['order']
      for game in self.game_list:
        self.content_panel.add_component(GameListElement(self.games[game]))
    
    else:
      # successfully got games from server + there are already games
      if server['order'] == self.game_list:
        for i, _id in enumerate(self.game_list):
          server_game = server['games'][_id]
          local_game = self.games[_id]
          if server_game['throws'] != local_game['throws']:
            self.content_panel.get_components()[i+1].update(server_game)
      # dumb way to repopulate for changed game list
      else:
        self.game_panel.clear()
        self.games = server['games']
        self.game_list = server['order']
        self.content_panel.add_component(GameListWall())
        for _id in self.game_list:
          self.game_panel.add_component(GameListElement(self.games[_id]))
        self.content_panel.add_component(GameListContacts())
    
  def logout_button_click (self, **event_args):
    # This method is called when the button is clicked
    anvil.users.logout()
    open_form('_login')

  def button_1_click (self, **event_args):
    # This method is called when the ADD CONTACTS button is clicked
    self.linear_panel_1.clear()
    self.linear_panel_1.add_component(AddContacts())
    self.linear_panel_2.get_components()[0].clear_highlights()

  def account_click (self, **event_args):
    # This method is called when the button is clicked
    open_form('_my_account')

