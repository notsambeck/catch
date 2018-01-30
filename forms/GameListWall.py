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
    
    # set self.me, self.you, self.am0
    self.me = user
    
    self.game_summary.visible = False
    self.wall_active = True
    self.num_throws.text = 'Throws: {}'.format(self.me['wall_throws'])
 
    self.set_event_handler('x-collapse', self.collapse)
    
  def expand(self, **event_args):
    # This method is called when the link is clicked
    # with Notification('Loading...'):
    self.parent.raise_event_on_children('x-collapse')
    self.game_view.visible = True
    self.game_summary.visible = False
    self.wall_active = True
    
  def collapse(self, **kwargs):
    if self.wall_active:
      throws = self.game_view.get_components()[0].throws
      # print(throws)
      resp = anvil.server.call_s('update_wall', throws)
      print('wall update confirmed')
      print(resp['success'])
    self.game_view.clear()
    self.game_summary.visible = True
    self.wall_active = False

  def game_view_show (self, **event_args):
    # This method is called when the linear panel is shown on the screen
    self.game_view.add_component(PlayCatch('wall', self.me))



