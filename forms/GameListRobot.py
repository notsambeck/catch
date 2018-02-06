from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables
from PlayCatch import PlayCatch

from datetime import datetime
import colors_day as colors
    
class GameListRobot (GameListRobotTemplate):
  '''
  GameListElement renders an entire row (game) as a status grid entry
  
  1 game per gameListElement instance
  '''
  def __init__(self, user, startup=False, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)
    
    # set self.me, self.you, self.am0
    self.me = user
    self.am0 = True
    self.you = 'CatchBot'
             
    # me: colors
    # print(self.me['color_1'])
    if self.me['color_1']:
      self.my_color_1 = self.me['color_1']
    else:
      self.my_color_1 = colors.black
    # print(self.me['color_2'])
    if self.me['color_2']:
      self.my_color_2 = self.me['color_2']
    else:
      self.my_color_2 = colors.skin

    self.set_event_handler('x-collapse', self.collapse)
    if startup:
      self.status_label.text = 'CATCHBOT   Throws: {}'.format(self.me['robot_throws'])
    else:
      self.status_label.text = 'CATCHBOT   Throws: {}'.format(get_open_form().robot_throws)
    self.status_label.foreground = colors.grass
      
  def set_labels(self):
    # clear
    self.background = colors.white
    self.status_label.text = 'CATCHBOT   Throws: {}'.format(get_open_form().robot_throws)
    
  def expand(self, **event_args):
    # This method is called when the link is clicked
    # with Notification('Loading game...'):
    # self.parent.raise_event_on_children('x-collapse')
    get_open_form().collapse_except_id('robot')
    self.child = PlayCatch('robot', self.me, self)
    self.game_view.add_component(self.child)
    self.game_summary.visible = False
    self.background = colors.white
    
  def collapse(self, x, **kwargs):
    if x == 'robot':
      # print('Collapse: not collapsing self')
      return
    self.game_view.clear()
    self.child = None
    self.game_summary.visible = True
    self.set_labels()
