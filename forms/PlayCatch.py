from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables

class PlayCatch (PlayCatchTemplate):
  def __init__(self, connection_id, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)
    self.connection_id = connection_id

    game = anvil.server.call('get_game_status', connection_id)

    player_has_ball = game['initiator_has_ball']
    self.friend_ball.selected = not player_has_ball
    self.player_ball.selected = player_has_ball
    self.throw_button.visible = player_has_ball
    
    self.friend_name.text = game['recipient']['username']
    self.player_name.text = game['initiator']['username']

  # navigation    

  def button_2_click (self, **event_args):
    # This method is called when the button is clicked
    open_form('GameList')

  def add_contacts_click (self, **event_args):
    # This method is called when the button is clicked
    open_form('AddContacts')

  def throw_button_click (self, **event_args):
    # This method is called when the button is clicked
    anvil.server.call('throw', self.connection_id)
    self.player_ball.selected = False
    self.friend_ball.selected = True
    self.throw_button.visible = False
