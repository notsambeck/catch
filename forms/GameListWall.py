from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables
from PlayCatch import PlayCatch

import colors
    
class GameListWall(GameListWallTemplate):
  '''
  GameListElement renders an entire row (game) as a status grid entry
  '''
  def __init__(self, user, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)
    self.set_event_handler('x-collapse', self.collapse)
    
    # set self.me, self.you, self.am0
    self.me = user
    self.throws = self.me['wall_throws']
    
    self.game_summary.visible = False
    self.game_view.visible = False
    self.wall_active = True
    self.num_throws.text = 'WALL!      Throws: {}'.format(self.throws)
 
    if self.me['color_1']:
      self.my_color_1 = self.me['color_1']
    else:
      self.my_color_1 = colors.black
    if self.me['color_2']:
      self.my_color_2 = self.me['color_2']
    else:
      self.my_color_2 = colors.skin
    print('GameListWall', self.my_color_1)

    self.expand()
    
  def expand(self, **event_args):
    # This method is called when the link is clicked
    # with Notification('Loading...'):
    if self.parent:
      self.parent.raise_event_on_children('x-collapse')
    self.game_view.visible = True
    self.game_summary.visible = False
    self.child = PlayCatch('wall', self.me, self)
    self.game_view.add_component(self.child)
    self.wall_active = True
    
  def collapse(self, **kwargs):
    if self.wall_active:
      self.throws = self.child.throws
      # print(throws)
      anvil.server.call_s('update_wall', self.throws)
    self.num_throws.text = 'WALL!      Throws: {}'.format(self.throws)
    self.game_view.clear()
    self.game_summary.visible = True
    self.wall_active = False
