from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables

    
class GameListElement(GameListElementTemplate):
  '''
  Game grid renders an entire row (game) as a status grid entry
  
  1 game per gameListElement instance
  '''
  def __init__(self, game, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)
    
    # self.game is ENTIRE ROW!
    self.game = game
    self.user_is_player_1 = self.game['player_1'] == anvil.users.get_user()

    if self.user_is_player_1:
      self.friend_label.text = self.game['player_2']['handle']
    else:
      self.friend_label.text = self.game['player_1']['handle']
    
    if self.game['is_active']:
      self.play_button.text = 'Go to game'
      if self.user_is_player_1:
        self.friend_ball.selected = self.game['who_has_ball'] == 2
        self.player_ball.selected = self.game['who_has_ball'] == 1
      else:
        self.friend_ball.selected = self.game['who_has_ball'] == 1
        self.player_ball.selected = self.game['who_has_ball'] == 2
        
      if self.game['throws'] >= 1:
        self.num_throws.visible = True
        self.num_throws.text = 'Throws: {}'.format(str(self.game['throws']))

      if (self.game['who_has_ball'] == 1 and self.user_is_player_1) or \
      (self.game['who_has_ball'] == 2 and not self.user_is_player_1):
        self.play_button.background = '#92bf89'
      else:
        self.play_button.background = '#CCCCCC'
      
    elif game['player_2_enabled']:  # game inactive but ready
      self.play_button.text = 'Start new game'
      self.friend_ball.visible = False
      self.player_ball.visible = False
      self.play_button.background = '#92bf89'
      
    else:   # player 2 not yet enabled
      self.play_button.text = 'Account not activated'
      self.friend_label.text = self.game['player_2']['phone_hash']

      self.play_button.enabled = False
      self.friend_ball.visible = False
      self.player_ball.visible = False
      self.play_button.background = '#CCCCCC'


  def play_button_click(self, **event_args):
    # This method is called when the button is clicked
    with Notification('starting game', timeout=1):
      open_form('PlayCatch', self.game)
