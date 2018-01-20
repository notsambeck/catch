from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables
from Status import Status

# TODO delete this and function definition in ServerModule1
# random_id = anvil.server.call('some_connection')

class PlayCatch (PlayCatchTemplate):
  def __init__(self, game, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)
    
    self.column_panel_1.add_component(Status())

    self.game = game
    if not self.game['is_active']:
      activate = anvil.server.call('make_game_active', self.game.get_id())
      assert activate['success']
      self.game = activate['game']

    self.user_is_player_1 = self.game['player_1'] == anvil.users.get_user()
    
    if self.game['has_ball'] == 0:
      self.player_1_ball.selected = True
      self.player_2_ball.selected = False
      if self.user_is_player_1:
        self.player_1_throw.visible = True
        self.player_2_throw.visible = False
      else:
        self.player_1_throw.visible = False
        self.player_2_throw.visible = False
    else: # 2 has ball
      self.player_1_ball.selected = False
      self.player_2_ball.selected = True
      if self.user_is_player_1:
        self.player_1_throw.visible = False
        self.player_2_throw.visible = False
      else:
        self.player_1_throw.visible = False
        self.player_2_throw.visible = True
    
    self.player_1_name.text = self.game['player_0']['handle']
    self.player_2_name.text = self.game['player_1']['handle']
    
    self.counter = 0
    self.ball_moving = False
    if self.game['has_ball'] == 0:
      self.ball_x = .12
      self.ball_vx = .04
    else:
      self.ball_x = .88
      self.ball_vx = .04
    self.ball_y = .76
    self.ball_vy = .06

  # navigation    

  def button_2_click(self, **event_args):
    # This method is called when the button is clicked
    open_form('GameList')

  def add_contacts_click(self, **event_args):
    # This method is called when the button is clicked
    open_form('AddContacts')

  def throw_button_click(self, **event_args):
    # tell server that ball has been thrown immediately
    throw_status = anvil.server.call('throw', self.game.get_id())
    if not throw_status['success']:
      print('Throw failed:', throw_status['msg'])
    elif throw_status['game'] == self.game:
      print('game state  unchanged... is it a pointer: {}'.format(throw_status['game'] is self.game))
    else:
      print('throw worked.')
    self.ball_y = .76
    self.ball_vy = .06
    
    # change indicators
    self.player_1_ball.selected = False
    self.player_2_ball.selected = False
    self.player_1_throw.visible = False
    self.player_2_throw.visible = False

    # change ball status so it starts moving
    self.ball_moving = True
    self.ball_steps = 0
    
  def ball_arrived(self):
    self.ball_moving = False
    if self.game['has_ball'] == 1:
      self.player_2_ball.selected = True
      if not self.user_is_player_1:
        self.player_2_button.visible = True
      self.game['has_ball'] == 2
    else:  
      self.player_1_ball.selected = True
      if self.user_is_player_1:
        self.player_1_button.visible = True
      self.game['who_has_ball'] == 1

      
  def draw(self, **event_args):
    self.counter += 1
    self.counter = self.counter % 500
    
    # This method is called Every [interval] seconds
    c = self.canvas_1
    w = c.get_width()
    h = c.get_height()
    
    c.clear_rect(0, 0, w, h * 2//3)
    
    # clouds
    c.fill_style = "rgba(255,255,255,.3)"
    for cloud in ((100, 20, 4, 0), (77, 45, 5, 30), (30, 120, 5, 40), (50, 120, 4, 63), (188, 103, 8, 90),
                 (100, 60, 2, 0), (230, 405, 5, 10), (70, 200, 3, 70), (160, 60, 7, 23), (218, 39, 2, 60),
                 (100, 60, 2, 80), (230, 405, 5, 50), (70, 200, 3, 40), (160, 60, 7, 53), (218, 39, 2, 95)):
      x = (cloud[3] - self.counter) * w // 500
      if x < 0:
        x += w
      c.fill_rect(x, h // cloud[2], cloud[0], cloud[1])
      
    for cloud in ((100, 20, 4, 0), (77, 45, 5, 30), (30, 120, 5, 40), (50, 120, 4, 63), (188, 103, 8, 90),
                 (100, 60, 2, 0), (230, 405, 5, 10), (70, 200, 3, 70), (160, 60, 7, 23), (218, 39, 2, 60),
                 (100, 60, 2, 80), (230, 405, 5, 50), (70, 200, 3, 40), (160, 60, 7, 53), (218, 39, 2, 95)):
      x = (cloud[3] - self.counter) * w // 400
      if x < -100:
        x += w
      c.fill_rect(x, h/2 // cloud[2], cloud[0], cloud[1])
      
    # city
    c.fill_style = "rgba(100,100,100,1)"
    c.fill_rect(300, h/3, w//18, h//2)
    c.fill_rect(220, .35*h, w//20, 2*h//3)
    c.fill_rect(320, .25*h, w//60, h//2.2)
    c.fill_rect(400, .5*h, w//15, h//1.6)
    c.fill_rect(490, .35*h, w//26, 2*h//3.7,)
    c.fill_rect(650, .25*h, w//40, h//2.7,)
    c.fill_rect(200, h/3, w//30, h//2.1)
    c.fill_rect(520, .35*h, w//20, 3*h//5)
    c.fill_rect(620, .25*h, w//40, h//2)
    c.fill_rect(700, .5*h, w//45, h//3)
    c.fill_rect(190, .35*h, w//36, 2*h//3.2,)
    c.fill_rect(50, .25*h, w//30, h//2.6,)
    
    c.fill_style = "rgba(60,60,90,1)"
    c.fill_rect(330, h/3, w//18, h//2)
    c.fill_rect(260, .35*h, w//20, 2*h//3)
    c.fill_rect(330, .25*h, w//60, h//2.2)
    c.fill_rect(440, .5*h, w//15, h//1.6)
    c.fill_rect(520, .35*h, w//26, 2*h//3.7,)
    c.fill_rect(670, .25*h, w//40, h//2.7,)
    c.fill_rect(230, h/3, w//30, h//2.1)
    c.fill_rect(560, .35*h, w//20, 3*h//5)
    c.fill_rect(630, .25*h, w//40, h//2)
    c.fill_rect(720, .5*h, w//45, h//3)
    c.fill_rect(210, .35*h, w//36, 2*h//3.2,)
    c.fill_rect(80, .25*h, w//30, h//2.6,)
    
    # trees
    c.fill_style = "rgba(100,140,70,1)"
    c.fill_rect(0, .6*h, w, h//2)
    
    # ground
    c.fill_style = "rgba(140,160,90,1)"
    c.fill_rect(0, h*2//3, w, h//3)
    
    # players
    c.fill_style = "rgba(0,0,0,1)"
    c.fill_rect(.1*w, .65*h, .04*w, .25*h )
    c.fill_rect(.9*w, .65*h, .04*w, .25*h )
    c.fill_style = '#BB9900'
    c.fill_rect(.1*w, .59*h, .04*w, .08*h )
    c.fill_rect(.9*w, .59*h, .04*w, .08*h )
    
    # if player has ball:
    c.fill_style = '#FFFFFF'
    if self.ball_moving:
      self.ball_steps += 1
      
      # direction
      if self.game['who_has_ball'] == 1:
        self.ball_x += self.ball_vx
      else:
        self.ball_x -= self.ball_vx
        
      self.ball_y -= self.ball_vy
      self.ball_vy -= .0064
      if self.ball_steps == 19:
        self.ball_arrived()
    c.fill_rect(self.ball_x * w, self.ball_y * h, .024*w, .05*h )
        
    if self.counter % 30 == 29 and not self.ball_moving:
      new_game = anvil.server.call('get_game_status', self.game.get_id())
      if new_game != self.game:
        self.game = new_game
        self.ball_moving = True
        self.ball_steps = 0
        self.ball_vy = .06

    

