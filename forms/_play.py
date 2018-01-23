from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables
from GameListContacts import GameListContacts
from GameListElement import GameListElement
from GameListWall import GameListWall

import colors

class _play (_playTemplate):
  def __init__(self, game=None, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)

    # Any code you write here will run when the form opens.

    self.top_contacts.visible = False
    
    name = anvil.users.get_user()['handle']
    self.handle.text = 'logged in as: {}'.format(name)  # menu bar
    
    self.content_panel.add_component(GameListWall())
    
    self.games = None
    self.game_views = {}
    self.game_list = []
    self.update_connections()
    
    self.content_panel.add_component(GameListContacts())
    self.top_contacts.add_component(GameListContacts())
    
  def update_connections(self):
    server = anvil.server.call_s('get_games')
    
    if not server['success']:
      print server['msg']
      return None
    
    elif not self.game_list:
      self.games = server['games']
      self.game_list = server['order']
      for _id in self.game_list:
        self.game_views[_id] = GameListElement(self.games[_id])
        self.content_panel.add_component(self.game_views[_id])
    
    else:
      # successfully got games from server + there are already games
      if server['order'] == self.game_list:
        for i, _id in enumerate(self.game_list):
          server_game = server['games'][_id]
          local_game = self.games[_id]
          if server_game['throws'] != local_game['throws']:
            self.game_views[_id].update(server_game)
      
      # we have games; there are updated games. Clear and start over
      else:
        self.content_panel.clear()
        self.games = server['games']
        self.game_list = server['order']
        self.content_panel.add_component(GameListWall())
        for _id in self.game_list:
          self.game_views[_id] = GameListElement(self.games[_id])
          self.content_panel.add_component(self.game_views[_id])
        self.content_panel.add_component(GameListContacts())
    
  def logout_button_click (self, **event_args):
    # This method is called when the button is clicked
    anvil.users.logout()
    open_form('_login')

  def button_1_click (self, **event_args):
    # This method is called when the ADD CONTACTS button is clicked
    self.top_contacts.visible = not self.top_contacts.visible
    if self.top_contacts.visible:
      self.button_1.background = colors.gray
    else:
      self.button_1.background = colors.highlight
    
    self.top_contacts.get_components()[0].expand()

  def account_click (self, **event_args):
    # This method is called when the button is clicked
    open_form('_my_account')

  def timer_1_tick(self, **event_args):
    # This method is called Every [interval] seconds
    self.update_connections()



