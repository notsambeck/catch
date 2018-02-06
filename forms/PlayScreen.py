from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables
from GameListContacts import GameListContacts
from GameListElement import GameListElement
from GameListWall import GameListWall
from GameListRobot import GameListRobot
from AddContacts import AddContacts

from utils import ErrorHandler

import colors_day as colors

class PlayScreen (PlayScreenTemplate):
  def __init__(self, user, game=None, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)

    self.error_handler = ErrorHandler(alert, open_form, user.get_id())
    set_default_error_handling(self.error_handler)
    
    self.me = user
    name = self.me['handle']
    self.wall_throws = self.me['wall_throws']
    self.robot_throws = self.me['robot_throws']
    self.handle.text = 'user: {}'.format(name)   # for menu bar
    self.active_view = 'wall'
    
    self.update_loop = 0   # quick update counter
    
  def update_connections(self):
    quick = bool(self.update_loop % 20)
    self.update_loop += 1

    try:
      server = anvil.server.call_s('get_games',
                                   robot_throws=self.robot_throws,
                                   wall_throws=self.wall_throws,
                                   quick=quick)
    except anvil.server.SessionExpiredError:
      print('starting EXCEPT on PlayScreen:')
      self.timer_1.interval = 100
      open_form('PleaseRefresh')
      return
    
    self.wall_throws = max(self.wall_throws, server['wall_throws'])
    self.robot_throws = max(self.robot_throws, server['robot_throws'])

    # print(server['msg'])    # retrieved n games
    if not server['success']:
      print('update failed', server['msg'])
      return None
    
    else:
       
      # successfully got games from server + there are already games
      if server['order'] == self.game_list[2:-1]:  # game_list includes wall and bottom_contacts
        for _id in server['order']:
          server_game = server['games'][_id]
          self.game_views[_id].update(server_game)
        # print('quick updated game_list')
        
      # local game_list is out of date. Clear and start over
      else:
        # do the following except for initial load with only wall

        if self.game_list != ['wall', 'robot']:
          self.content_panel.clear()
          self.game_views['wall'] = GameListWall(self.me)
          self.content_panel.add_component(self.game_views['wall'])                
          self.game_views['robot'] = GameListRobot(self.me)
          self.content_panel.add_component(self.game_views['robot'])
          startup = False
        else:
          startup = True
        
        for _id in server['order']:
          self.game_views[_id] = GameListElement(self.me, server['games'][_id])  # make the panel
          self.content_panel.add_component(self.game_views[_id])            # attach to this form
        
        self.game_views['bottom_contacts'] = GameListContacts()
        self.content_panel.add_component(self.game_views['bottom_contacts'])
        
        self.game_list = ['wall', 'robot'] + server['order'] + ['bottom_contacts']
        
        if not startup:
          self.game_views[self.active_view].expand()
        # print('made new game_list')
        
  def add_game(self, game):
    # game has been added at the server; just update from there as per usual
    self.update_loop = 0
    self.timer_1_tick()
    
  def logout_button_click (self, **event_args):
    # This method is called when the button is clicked   
    self.timer_1.remove_from_parent()
    print('calling do_logout')
    anvil.server.call('do_logout')
    open_form('LoginScreen')

  def account_click (self, **event_args):
    # This method is called when the button is clicked
    open_form('MyAccountScreen')

  def timer_1_tick(self, **event_args):
    # This method is called Every [interval] seconds
    self.update_connections()

  def content_panel_show (self, **event_args):
    # This method is called when the column panel is shown on the screen
    self.game_list = ['wall', 'robot']   # list of game_ids IN DISPLAY ORDER
    self.game_views = {'wall': GameListWall(self.me, startup=True),
                       'robot': GameListRobot(self.me, startup=True)}
    self.content_panel.add_component(self.game_views['wall'])
    self.content_panel.add_component(self.game_views['robot'])
    
    self.update_connections()
    
  def collapse_except_id(self, game_id):
    # this is ~40x faster than iterating through children
    
    # formerly: self.parent.raise_event_on_children('x-collapse')
    # print('collapse_except_id({})'.format(game_id))
    self.content_panel.raise_event_on_children('x-collapse', x=game_id)