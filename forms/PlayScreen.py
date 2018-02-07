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
    
    self.game_list = []
    self.game_views = {}
    
    self.update_loop = 0   # quick update counter
    
  def update_connections(self):
    quick = bool(self.update_loop % 10)
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
 
    # print(server['msg'])    # retrieved n games
    if not server['success']:
      print('update failed', server['msg'])
      return None
    
    # update non-PvP games
    self.wall_throws = max(self.wall_throws, server['wall_throws'])
    self.robot_throws = max(self.robot_throws, server['robot_throws'])
    
    if not server['order']:   # if there are 0 PvP games
      return None
    
    # successfully got games from server
    if not self.main_panel.visible:
      self.main_panel.visible = True
    
    if server['order'] == self.game_list:  # if they are unchanged: update each
      for _id in server['order']:
        server_game = server['games'][_id]
        self.game_views[_id].update(server_game)
      # print('quick updated game_list') 
      return True
    
    # local game_list is out of date. 
    print('full PlayScreen update starting')
    position = 0   # position in rendered game views
    popped = set()
    
    for game_id in server['order']:
      if position < len(self.game_list) and game_id == self.game_list[position]:
        print('already ordered')
        self.game_views[game_id].update(server['games'][game_id])
        position += 1
      
      else:
        if game_id in popped:
          print('push game: {}'.format(game_id))
          self.main_panel.add_component(self.game_views[game_id])
          popped.remove(game_id)
          self.game_views[game_id].update(server['games'][game_id])

        elif self.game_views.get(game_id, False):
          # server order calls for a game that is rendered out of order
          print('game {} exists, digging for it...'.format(game_id))
          while game_id != self.game_list[position]:
            out_of_order = self.game_list[position]
            print('popping game: {}'.format(out_of_order))
            self.game_views[out_of_order].remove_from_parent()
            popped.add(out_of_order)
            position += 1
          print('dig complete; updating')
          self.game_views[game_id].update(server['games'][game_id])
          position += 1

        else:  # build new game
          print('add new game {}'.format(game_id))
          self.game_views[game_id] = GameListElement(self.me, server['games'][game_id])
          self.main_panel.add_component(self.game_views[game_id])
          
    if len(popped):
      print(popped)
    self.game_list = server['order']

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
    self.game_views = {'wall': GameListWall(self.me, startup=True),
                       'robot': GameListRobot(self.me, startup=True),
                       'contacts': GameListContacts()}
    self.footer_panel.add_component(self.game_views['contacts'])
    self.header_panel.add_component(self.game_views['wall'])
    self.header_panel.add_component(self.game_views['robot'])
    self.footer_panel.visible = True
    self.header_panel.visible = True
    
    self.update_connections()
    
  def collapse_except_id(self, game_id):
    # this is ~40x faster than iterating through children

    self.main_panel.raise_event_on_children('x-collapse', x=game_id)
    self.header_panel.raise_event_on_children('x-collapse', x=game_id)
    self.footer_panel.raise_event_on_children('x-collapse', x=game_id)
    