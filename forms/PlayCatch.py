from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables

# TODO delete this and function definition in ServerModule1
random_id = anvil.server.call('some_connection')

class PlayCatch (PlayCatchTemplate):
  def __init__(self, connection_id=random_id, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)
    self.connection_id = connection_id
    self.counter = 0

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

  def draw (self, **event_args):
    self.counter += 1
    self.counter = self.counter % 100
    
    # This method is called Every [interval] seconds
    c = self.canvas_1
    w = c.get_width()
    h = c.get_height()
    
    c.clear_rect(0, 0, w, h * 2//3)
    
    # ground
    c.fill_style = "rgba(100,200,50,1)"
    c.fill_rect(0, h*2//3, w, h//3)
    
    # clouds
    c.fill_style = "rgba(255,255,255,.3)"
    for cloud in ((100, 20, 4, 0), (77, 45, 5, 30), (30, 120, 5, 40), (50, 120, 4, 63), (188, 103, 8, 90),
                 (100, 60, 2, 0), (230, 405, 5, 10), (70, 200, 3, 70), (160, 60, 7, 23), (218, 39, 2, 60)):
      x = (cloud[3] - self.counter) * w // 100
      if x < 0:
        x += w
      c.fill_rect(x, h // cloud[2], cloud[0], cloud[1])
      

