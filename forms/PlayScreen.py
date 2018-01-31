from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables
from GameListContacts import GameListContacts
from GameListElement import GameListElement
from GameListWall import GameListWall

import colors


def error_handler(err):
  # TODO: change this behaviour for release
  Notification(str(err), title='Error bypassed').show()
  open_form('LoginScreen')


class PlayScreen (PlayScreenTemplate):
  def __init__(self, user, game=None, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)

    self.top_contacts.visible = False
    
    self.me = user
    name = self.me['handle']
    self.handle.text = 'user: {}'.format(name)   # for menu bar
    print(name)
    
    self.games = None
    self.game_views = {}
    self.game_list = []

    self.top_contacts.add_component(GameListContacts())
    
    set_default_error_handling(error_handler)
    
  def update_connections(self):
    try:
      server = anvil.server.call_s('get_games')
    except anvil.server.SessionExpiredError:
      print('session expired; resetting session')
      anvil.server.reset_session()
      anvil.server.call('start_session')
      server = anvil.server.call_s('get_games')

    
    print(server['msg'])  # retrieved 5 games
    if not server['success']:
      print('update failed', server['msg'])
      return None
    
    elif not self.game_list:
      self.games = server['games']
      self.game_list = server['order']
      for _id in self.game_list:
        self.game_views[_id] = GameListElement(self.me, self.games[_id])
        self.content_panel.add_component(self.game_views[_id])
      print('made new game list')    
      
    else:
      # successfully got games from server + there are already games
      if server['order'] == self.game_list:
        for _id in self.game_list:
          server_game = server['games'][_id]
          # local_game = self.games[_id]
          # if server_game['throws'] != local_game['throws']:   # update only after throws
          self.game_views[_id].update(server_game)
        print('quick updated game_list')
      # we have games; there are updated games. Clear and start over
      else:
        self.content_panel.clear()
        self.games = server['games']
        self.game_list = server['order']
        self.content_panel.add_component(GameListWall(self.me))
        for _id in self.game_list:
          self.game_views[_id] = GameListElement(self.me, self.games[_id])  # make the panel
          self.content_panel.add_component(self.game_views[_id])            # attach to this form
        self.content_panel.add_component(GameListContacts())
        print('updated game_list')
    
  def logout_button_click (self, **event_args):
    # This method is called when the button is clicked    
    anvil.server.call('delete_cookie')
    anvil.users.logout()
    open_form('LoginScreen')

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
    open_form('MyAccountScreen')

  def timer_1_tick(self, **event_args):
    # This method is called Every [interval] seconds
    self.update_connections()

  def content_panel_show (self, **event_args):
    # This method is called when the column panel is shown on the screen
    self.content_panel.add_component(GameListWall(self.me))
    
    self.update_connections()
    self.content_panel.add_component(GameListContacts())
