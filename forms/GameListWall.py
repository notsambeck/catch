from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables
from PlayCatch import PlayCatch

import colors_day as colors
    
class GameListWall(GameListWallTemplate):
  '''
  GameListElement renders an entire row (game) as a status grid entry
  '''
  def __init__(self, user, startup=False, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)
    
    # set self.me, self.you, self.am0
    self.me = user
    
    self.game_summary.visible = False
    self.game_view.visible = False
    self.wall_active = True
    

    self.num_throws.foreground = colors.grass
    
    self.set_event_handler('x-collapse', self.collapse)
 
    if self.me['color_1']:
      self.my_color_1 = self.me['color_1']
    else:
      self.my_color_1 = colors.black
    if self.me['color_2']:
      self.my_color_2 = self.me['color_2']
    else:
      self.my_color_2 = colors.skin
      
    if startup:
      self.game_view.visible = True
      self.game_summary.visible = False
      self.child = PlayCatch('wall', self.me, self)
      self.game_view.add_component(self.child)
      self.num_throws.text = 'WALL     Throws: {}'.format(self.me['wall_throws'])
    else:
      self.num_throws.text = 'WALL     Throws: {}'.format(get_open_form().wall_throws)

    # print('GameListWall', self.my_color_1)

    
  def expand(self, **event_args):
    # This method is called when the link is clicked
    # with Notification('Loading...'):
    get_open_form().collapse_except_id('wall')
    self.game_view.visible = True
    self.game_summary.visible = False
    self.child = PlayCatch('wall', self.me, self)
    self.game_view.add_component(self.child)
    self.wall_active = True
    
  def collapse(self, x, **kwargs):
    if x == 'wall':
      # print('Collapse: not collapsing self')
      return
    self.num_throws.text = 'WALL     Throws: {}'.format(get_open_form().wall_throws)
    self.game_view.clear()
    self.game_summary.visible = True
    self.wall_active = False
