from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables
from PlayCatch import PlayCatch

from datetime import datetime
import colors
    
class GameListElement(GameListElementTemplate):
  '''
  GameListElement renders an entire row (game) as a status grid entry
  
  1 game per gameListElement instance
  '''
  def __init__(self, game, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)
    
    # self.game is ENTIRE ROW!
    self.game = game
    
    # set self.me, self.you, self.am0
    self.me = anvil.users.get_user()
    self.am0 = self.game['player_0'] == self.me
    if self.am0:
      self.you = self.game['player_1']['handle']
      if not self.you:
        self.you = self.game['player_1']['phone_hash']
    else:
      self.you = self.game['player_0']['handle']
      if not self.you:
        self.you = self.game['player_0']['phone_hash']

    self.set_labels()
    
    self.set_event_handler('x-collapse', self.collapse)
    
  def set_labels(self):
    # clear
    self.background = colors.white
 
    # Normal status for ongoing game
    if self.game['is_active']:
      time = self.game['last_throw_time']
      now = datetime.now()
      if time.day == now.day and time.month == now.month:
        timestring = 'at {}:{:02d}'.format(time.month, time.day, time.hour, time.minute)
      else:
        timestring = '{}/{} at {}:{:02d}'.format(time.month, time.day, time.hour, time.minute)
      if (self.am0 and self.game['has_ball'] == 0) or (not self.am0 and self.game['has_ball'] == 1):
        self.status_label.text = '{} threw you ball #{} at {}'.format(self.you,
                                                                      self.game['throws'],
                                                                      timestring,)
        self.status_label.foreground = colors.highlight
      else:
        self.status_label.text = 'You threw ball #{} to {} at {}'.format(self.game['throws'],
                                                                         self.you,
                                                                         timestring,)
        self.status_label.foreground = colors.off

    # game inactive but both ready
    elif self.game['p1_enabled']:  
      self.status_label.text = 'Start new game with {}!'.format(self.you)
      self.status_label.foreground = colors.black
      self.background = colors.highlight

    # player 2 not yet enabled      
    else:
      self.status_label.text = 'Player {} not activated'.format(self.you)
      self.status_label.foreground = colors.gray
   
  def update(self, updated_game):
    if self.game['throws'] != updated_game['throws'] or self.game['p1_enabled'] != updated_game['p1_enabled']:
      self.game = updated_game
      self.set_labels()

  def expand(self, **event_args):
    if not self.game['p1_enabled']:
      return False
    # This method is called when the link is clicked
    with Notification('Loading game...'):
      self.parent.raise_event_on_children('x-collapse')
      self.game_view.add_component(PlayCatch(self.game))
      self.game_summary.visible = False
      self.background = colors.white
      
  def collapse(self, **kwargs):
    self.game_view.clear()
    self.game_summary.visible = True
