from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables

class GameGrid (GameGridTemplate):
  def __init__(self, row, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)
    self.row = row
    
    # self.connection_id is the connection with logged in user as P1
    self.connection_id = self.row.get_id()

    self.recipient_label.text = self.row['recipient']['username']
    self.player_ball.selected = self.row['initiator_has_ball']
    self.friend_ball.selected = self.row['dual']['initiator_has_ball']
      
      
    if self.row['game_ongoing']:
      self.play_button.text = 'Return to game'
      self.label_ongoing.visible = True
    else:
      self.play_button.text = 'Start new game'
      self.label_ongoing.visible = False

      
  def play_button_click(self, **event_args):
    # This method is called when the button is clicked
    open_form('PlayCatch', self.connection_id)



