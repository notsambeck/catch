from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables

    
class GameGrid(GameGridTemplate):
  '''
  Game grid renders an entire row (connection) as a status grid entry
  User on the left, opponent on the right!'''
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
      
    else:  # game inactive
      self.play_button.text = 'Start new game'
      self.friend_ball.visible = False
      self.player_ball.visible = False
      self.play_button.background = '#92bf89'


  def play_button_click(self, **event_args):
    # This method is called when the button is clicked
    with Notification('starting game', timeout=1):
      open_form('PlayCatch', self.game)
