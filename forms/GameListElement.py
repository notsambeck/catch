from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables
from PlayCatch import PlayCatch

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

    self.you_label.text = self.you
    
    self.set_labels()
    
    self.set_event_handler('x-collapse', self.collapse)
    
  def set_labels(self):
    # clear
    self.background = colors.white
 
    # Normal status for ongoing game
    if self.game['is_active']:
      self.play_button.visible = False
      self.status_label.visible = True
      
      if (self.am0 and self.game['has_ball'] == 0) or (not self.am0 and self.game['has_ball'] == 1):
        self.status_label.text = '{} threw you the ball'.format(self.you)
        self.status_label.foreground = colors.highlight
      else:
        self.status_label.text = 'you threw ball to {}'.format(self.you)
        self.status_label.foreground = colors.off
        
      self.num_throws.visible = True
      self.num_throws.text = 'Throws: {}'.format(str(self.game['throws']))

    elif self.game['p1_enabled']:  # game inactive but both ready
      self.play_button.text = 'Start new game'
      self.play_button.enabled = True
      self.background = colors.highlight
      self.status_label.visible = False
      self.num_throws.visible = False
      
    else:   # player 2 not yet enabled
      self.play_button.text = 'Player not activated'
      self.play_button.foreground = colors.gray
      self.you_label.foreground = colors.gray
   
  def update(self, updated_game):
    if self.game['throws'] != updated_game['throws'] or self.game['p1_enabled'] != updated_game['p1_enabled']:
      self.game = updated_game
      self.set_labels()

  def expand(self, **event_args):
    if not self.game['p1_enabled']:
      return False
    # This method is called when the link is clicked
    with Notification('Loading...'):
      self.parent.raise_event_on_children('x-collapse')
      self.game_view.add_component(PlayCatch(self.game))
      self.game_summary.visible = False
      
  def collapse(self, **kwargs):
    self.game_view.clear()
    self.game_summary.visible = True
