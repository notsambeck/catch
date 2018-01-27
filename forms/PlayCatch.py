from anvil import *
import anvil.server
import anvil.users
import random

# TODO following function call and definition in ServerModule for deployment?
# random_id = anvil.server.call('some_connection')

# city


class PlayCatch (PlayCatchTemplate):
  def __init__(self, game, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)
    
    self.me = anvil.users.get_user()
    self.game = game
    
    if not self.game['is_active']:
      activate = anvil.server.call_s('make_game_active', self.game.get_id())
      assert activate['success']
      self.game = activate['game']

    # set permanent labels for this game instance:
    
    self.am0 = self.game['player_0'] == self.me
    
    self.counter = 0
    self.buildings = []

    self.set_labels_directions()    
    
  def make_buildings(self):
    self.width = self.canvas_1.get_width()
    self.height = self.canvas_1.get_height()
    for _ in range(10):
      self.make_building()
    
    print(self.width, self.height, self.canvas_1.width, self.canvas_1.height)
      
  def make_building(self):
    '''make random building w x h'''
    bx = random.randrange(0, self.width)    # center
    bh = random.randrange(0, self.height//2)  # top
    bw = random.choice([.10, .15, .5, .7,])  # width
    self.buildings.append([bx, bh, bw])
    
  def draw_building(self, bx, bh, bw):
    self.canvas_1.fill_style = "rgba(100,100,100,1)"
    self.canvas_1.fill_rect(bx, bh, bw, self.height-bh)
    self.canvas_1.fill_style = "rgba(60,60,90,1)"
    self.canvas_1.fill_rect(bx-bw, bh, bw, self.height-bh)
      
  def set_labels_directions(self):
    if self.am0:
      self.i_have_ball = self.game['has_ball'] == 0
      if self.i_have_ball:
        self.p1_name.text = self.game['player_1']['handle']
      else:
        self.p1_name.text = '{} (has the ball)'.format(self.game['player_1']['handle'])
    else:
      self.i_have_ball = self.game['has_ball'] == 1
      if self.i_have_ball:
        self.p1_name.text = self.game['player_0']['handle']
      else:
        self.p1_name.text = '{} (has the ball)'.format(self.game['player_0']['handle'])

    self.p0_name.text = 'Me'

    # TODO: either unhide ball indicators or delete
    # self.p0_ball.selected = self.i_have_ball
    # self.p1_ball.selected = not self.i_have_ball
    
    # set movement vairables
    self.ball_moving = False
    
    if self.i_have_ball:
      self.ball_x = .12
      self.ball_vx = .04
    else:
      self.ball_x = .88
      self.ball_vx = -.04
      
    # set y / y_velocity
    self.ball_y = .76
    self.ball_vy = .06
 
  def throw_button_click(self, **event_args):
    if not self.i_have_ball:
      return False
    # tell server that ball has been thrown immediately
    throw_status = anvil.server.call_s('throw', self.game.get_id())
    
    if not throw_status['success']:
      print('Throw failed:', throw_status['msg'])
      return False
    else:
      self.game = throw_status['game']

    # reset y velocity
    self.ball_y = .76
    self.ball_vy = .06
    
    # change ball status so it starts moving
    self.ball_moving = True
    self.ball_steps = 0
    
  def ball_arrived(self):
    self.ball_moving = False
    self.set_labels_directions()
      
  def draw(self, **event_args):
    self.counter += 1
    self.counter = self.counter % 500
    
    # This method is called Every [interval] seconds
    c = self.canvas_1
    w = c.get_width()
    h = c.get_height()
    
    c.clear_rect(0, 0, w, h * 2//3)
    
    # clouds
    c.fill_style = "rgba(190,190,190,.25)"
    for cloud in ((100, 20, 4, 0), (77, 45, 5, 30), (30, 120, 5, 40), (50, 120, 4, 63), (188, 103, 8, 90),
                 (100, 60, 2, 0), (230, 405, 5, 10), (70, 200, 3, 70), (160, 60, 7, 23), (218, 39, 2, 60),
                 (100, 60, 2, 80), (230, 405, 5, 50), (70, 200, 3, 40), (160, 60, 7, 53), (218, 39, 2, 95)):
      x = (cloud[3] - self.counter) * w // 200
      if x < 0:
        x += w
      c.fill_rect(x, h // cloud[2], cloud[0], cloud[1])
    
    c.fill_style = "rgba(210,210,210,.2)"
    for cloud in ((100, 20, 4, 0), (77, 45, 5, 30), (30, 120, 5, 40), (50, 120, 4, 63), (188, 103, 8, 90),
                 (100, 60, 2, 0), (230, 405, 5, 10), (70, 200, 3, 70), (160, 60, 7, 23), (218, 39, 2, 60),
                 (100, 60, 2, 80), (230, 405, 5, 50), (70, 200, 3, 40), (160, 60, 7, 53), (218, 39, 2, 95)):
      x = (cloud[3] - self.counter) * w // 250
      if x < -100:
        x += w
      c.fill_rect(x, h/2 // cloud[2], cloud[0], cloud[1])
      
    for b in self.buildings:
      self.draw_building(b[0], b[1], b[2])

    # trees
    c.fill_style = "rgba(100,140,70,1)"
    c.fill_rect(0, .6*h, (w*1.2)//1, h//2)
    
    # ground
    c.fill_style = "rgba(140,160,90,1)"
    c.fill_rect(0, h*2//3, (w*1.2)//1, h//3)
    
    # players
    c.fill_style = "rgba(0,0,0,1)"
    c.fill_rect(.1*w, .65*h, .04*w, .25*h )
    c.fill_rect(.9*w, .65*h, .04*w, .25*h )
    c.fill_style = '#AA9900'
    # heads
    c.fill_rect(.1*w, .59*h, .04*w, .08*h )
    c.fill_rect(.9*w, .59*h, .04*w, .08*h )
    # gloves
    c.fill_rect(.12*w, .75*h, .03*w, .06*h )
    c.fill_rect(.88*w, .75*h, .03*w, .06*h )
    
    # ball:
    c.fill_style = '#FEF5E7'
    c.fill_rect(self.ball_x * w, self.ball_y * h, .024*w, .05*h )
    
    if self.i_have_ball and not self.ball_moving and self.counter % 5:
      c.fill_style = '#FFFFFF'
      c.font = '{}px sans-serif'.format(h//9)
      c.fill_text('TAP TO THROW', w//16, h//5)
    
    if self.ball_moving:
      self.ball_steps += 1
      
      # direction
      self.ball_x += self.ball_vx
        
      self.ball_y -= self.ball_vy   # indexed from top
      self.ball_vy -= .0067
      
      if self.ball_steps == 20:
        # print('ball has arrived')
        self.ball_arrived()
        
    # update from server
    if self.counter % 20 == 19 and not self.ball_moving:
      game_live = anvil.server.call_s('get_game', self.game.get_id())
      if game_live['success']:
        pass
        # print('local: {} / server: {}'.format(self.game['has_ball'], game_live['game']['has_ball']))
      else:
        print(game_live['msg'])
        
      if game_live['success'] and game_live['game']['has_ball'] != self.game['has_ball']:
        # print('updating from server...')
        self.game = game_live['game']
        self.ball_moving = True
        self.ball_steps = 0
        self.ball_vy = .06
