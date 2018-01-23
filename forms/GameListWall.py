from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables
from PlayWall import PlayWall

import colors
    
class GameListWall(GameListWallTemplate):
  '''
  GameListElement renders an entire row (game) as a status grid entry
  
  1 game per gameListElement instance
  '''
  def __init__(self, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)
    
    # set self.me, self.you, self.am0
    self.me = anvil.users.get_user()
    
    self.game_view.add_component(PlayWall())
        
    self.set_event_handler('x-collapse', self.collapse)
    
  def expand(self, **event_args):
    # This method is called when the link is clicked
    with Notification('Loading...'):
      self.parent.raise_event_on_children('x-collapse')
      self.game_view.add_component(PlayWall())
      self.game_summary.visible = False
      
  def collapse(self, **kwargs):
    self.game_view.clear()
    self.game_summary.visible = True
