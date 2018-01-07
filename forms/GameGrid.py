from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables

    
class GameGrid(GameGridTemplate):
  def __init__(self, connection_id, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)
    self.connection_id = connection_id

    self.game = anvil.server.call('get_game_status', connection_id)
    self.friend_label.text = self.game['recipient']['username']

        
    if self.game['game_ongoing']:
      self.play_button.text = 'Return to game'
      self.label_ongoing.visible = True
      self.friend_ball.selected = not self.game['initiator_has_ball']
      self.player_ball.selected = self.game['initiator_has_ball']
      if self.game['initiator_has_ball']:
        self.play_button.background = '#92bf89'
      else:
        self.play_button.background = '#CCCCCC'
      
    else:
      self.play_button.text = 'Start new game'
      self.label_ongoing.visible = False
      self.friend_ball.visible = False
      self.player_ball.visible = False
      self.play_button.background = '#92bf89'


  def play_button_click(self, **event_args):
    # This method is called when the button is clicked
    open_form('PlayCatch', self.connection_id)



