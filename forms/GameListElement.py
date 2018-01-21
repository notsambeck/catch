from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables

    
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
    self.am0 = self.game['player_0'] == anvil.users.get_user()

    if self.am0:
      self.friend_label.text = self.game['player_1']['handle']
    else:
      self.friend_label.text = self.game['player_0']['handle']
    
    self.set_labels()
    
  def set_labels(self):
    if self.game['is_active']:
      self.play_button.text = 'Go to game'
      if self.am0:
        self.friend_ball.selected = self.game['has_ball'] == 1
        self.player_ball.selected = self.game['has_ball'] == 0
      else:
        self.friend_ball.selected = self.game['has_ball'] == 0
        self.player_ball.selected = self.game['has_ball'] == 1
        
      if self.game['throws'] >= 1:
        self.num_throws.visible = True
        self.num_throws.text = 'Throws: {}'.format(str(self.game['throws']))

      if (self.game['has_ball'] == 0 and self.am0) or (self.game['has_ball'] == 1 and not self.am0):
        self.play_button.background = '#92bf89'
      else:
        self.play_button.background = '#CCCCCC'
      
    elif self.game['p1_enabled']:  # game inactive but both ready
      self.play_button.text = 'Start new game'
      self.friend_ball.visible = False
      self.player_ball.visible = False
      self.play_button.background = '#92bf89'
      
    else:   # player 2 not yet enabled
      self.play_button.text = 'Player not activated'
      self.friend_label.text = self.game['player_1']['phone_hash']

      self.play_button.enabled = False
      self.friend_ball.visible = False
      self.player_ball.visible = False
      self.play_button.background = '#CCCCCC'
 

  def play_button_click(self, **event_args):
    # This method is called when the button is clicked
    with Notification('Going to the park...', timeout=1):
      open_form('PlayCatch', self.game)
      
  def update(self, updated_game):
    if self.game['throws'] != updated_game['throws'] or self.game['p1_enabled'] != updated_game['p1_enabled']:
      self.game = updated_game
      self.set_labels()
