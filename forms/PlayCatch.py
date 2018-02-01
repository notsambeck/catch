from anvil import *
import anvil.server
import anvil.users
import random
import drawing
import colors

from utils import error_handler

# TODO: remove the related code from web_callable before deployment
# as it may be a minor security issue
# random_id = anvil.server.call('some_connection')

# city

class PlayCatch (PlayCatchTemplate):
  def __init__(self, game, me, wrapper, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)
    
    set_default_error_handling(error_handler)
    
    self.me = me
    self.game = game
    self.wrapper = wrapper
    
    if game != 'wall':
      if not self.game['is_active']:
        activate = anvil.server.call_s('make_game_active', self.game.get_id())
        assert activate['success']
        self.game = activate['game']

      self.am0 = self.game['player_0'] == self.me
      
    # else game == wall
    else:
      self.throws = self.wrapper.throws
    
    # motion loop counter
    self.counter = 0
    self.buildings = []

    self.set_labels()
    self.set_directions()
    
    self.skip_a_beat = True
    self.canvas_1.visible = True
  
  def set_directions(self):
    
    self.ball_moving = False
    # set y / y_velocity
    self.ball_y = .78
    self.ball_vy = .06

    if self.game == 'wall':
      self.ball_x = .12
      self.ball_vx = .04

    else:
      if self.am0:
        self.i_have_ball = self.game['has_ball'] == 0
      else:
        self.i_have_ball = self.game['has_ball'] == 1
      
      if self.i_have_ball:
        self.ball_x = .12
        self.ball_vx = .04
      else:
        self.ball_x = .88
        self.ball_vx = -.04

  def set_labels(self):
    self.my_color_1 = self.me['color_1']
    self.my_color_2 = self.me['color_2']
    
    if self.game == 'wall':
      return None
    
    self.p1_name = self.wrapper.you

    self.opp_color_1 = self.wrapper.opp_color_1
    self.opp_color_2 = self.wrapper.opp_color_2

  def throw_button_click(self, **event_args):
    if self.game == 'wall':
      return self.throw_wall()
    
    if not self.i_have_ball or self.ball_moving:
      return False
    # tell server that ball has been thrown immediately
    throw_status = anvil.server.call_s('throw', self.game.get_id())
    
    if not throw_status['success']:
      print('Throw failed:', throw_status['msg'])
      return False
    else:
      self.game = throw_status['game']
      self.wrapper.update(throw_status['game'])

    # reset y velocity
    self.ball_y = .78
    self.ball_vy = .06
    
    # change ball status so it starts moving
    self.ball_moving = True
    self.ball_steps = 0
    
  def throw_wall(self):
    if self.ball_moving:
      return False
    self.throws += 1
    self.wrapper.throws = self.throws
    if self.throws % 10 == 0:
      anvil.server.call_s('update_wall', self.throws)

    # reset y velocity
    self.ball_y = .78
    self.ball_vy = .06
    
    # change ball status so it starts moving
    self.ball_moving = True
    self.ball_steps = 0
    
  def ball_arrived(self):
    self.ball_steps = 0
    self.counter = 0
    self.ball_moving = False
    self.set_directions()
      
  def draw(self, **event_args):
    '''
    this method runs every clock tick (timer element on Design view)
    '''
    
    if not self.canvas_1.visible:
      return
    
    self.canvas_1.reset_context()

    # alias
    c = self.canvas_1
    
    self.counter += 1
    self.counter = self.counter % 500
    
    # clear the sky
    c.clear_rect(0, 0, self.w * 1.5, self.h * .65)
    
    for cloud in self.clouds:
      cloud.draw()
    
    for bld in self.buildings:
      bld.draw()
    
    # ground
    drawing.Rectangle(0, .6, 1.5, .5, colors.grass).draw()

    for tree in self.far_trees:
      tree.draw()
    
    # trees
    for tree in self.trees:
      tree.draw()
      
    drawing.RandomTree.update_wind()
    
    # body
    drawing.Rectangle(.1, .57, .04, .3, self.my_color_1).draw()
    # head
    drawing.Circle(.09, .57, .035, self.my_color_2).draw()
    # hand
    if self.ball_moving and self.ball_steps == 1:
      drawing.Circle(.12, .77, .025, self.my_color_2).draw()
    elif self.ball_moving and self.ball_steps == 2:
      drawing.Circle(.14, .75, .025, self.my_color_2).draw()
    else:
      drawing.Circle(.11, .79, .025, self.my_color_2).draw()
    
    # player1
    if self.game != 'wall':
      drawing.Rectangle(.9, .57, .04, .3, self.opp_color_1).draw()
      drawing.Circle(.88, .79, .025, self.opp_color_2).draw()
      drawing.Circle(.88, .57, .035, self.opp_color_2).draw()
    
    # wall: 
    if self.game == 'wall':
      # wall
      for delta in [.01 * i for i in range(8)]:
        drawing.Rectangle(.46 + delta * 2, .28 + delta, .03, .6, colors.red).draw()
        
      # end of wall
      drawing.Rectangle(.62, .36, .03, .6, colors.darkred).draw()
    
    c.fill_style = colors.white
    
    # ball:
    ball = drawing.Circle(self.ball_x, self.ball_y, .019).draw()

    # text:
    c.font = '{}px sans-serif'.format(self.h//10)
    
    pad = 6
    c.text_align = 'left'
    c.text_baseline = 'top'
    # tap to throw text
    if (self.game == 'wall' or self.i_have_ball) and not self.ball_moving and self.counter % 5:
      c.fill_text('TAP TO THROW', pad, pad)
    
    c.font = '{}px sans-serif'.format(self.h//16)
    c.text_align = 'right'
    c.text_baseline = 'bottom'

    if self.game == 'wall':
      c.fill_text('THROWS: {}'.format(self.throws), self.w - pad, self.h - pad)
    else:
      c.fill_text(self.p1_name, self.w - pad, self.h - pad)
      c.text_align = 'left'
      c.fill_text('Me', pad, self.h - pad)
    
    # move ball: not wall
    if self.ball_moving and not self.game == 'wall':
      self.ball_steps += 1
      
      # direction
      self.ball_x += self.ball_vx
        
      self.ball_y -= self.ball_vy   # indexed from top
      self.ball_vy -= .0067
      
    # move ball: wall
    elif self.ball_moving:
      self.ball_steps += 1
      
      # direction
      if self.ball_steps < 10:
        self.ball_x += self.ball_vx
      else:
        self.ball_x -= self.ball_vx
        
      self.ball_y -= self.ball_vy   # indexed from top
      self.ball_vy -= .007

    # check arrival
    if self.ball_moving:
      if self.ball_steps == 20:
        self.ball_arrived()
      elif self.game == 'wall' and self.ball_steps == 19:
        self.ball_arrived()

    # update from server
    if self.game != 'wall' and self.counter % 30 == 29 and not self.ball_moving and not self.i_have_ball:
      game_live = anvil.server.call_s('get_game', self.game.get_id())
      if not game_live['success']:
        print(game_live['msg'])
        
      if game_live['success'] and game_live['game']['has_ball'] != self.game['has_ball']:
        # print('updating from server...')
        self.game = game_live['game']
        self.ball_moving = True
        self.ball_steps = 0
        self.ball_vy = .06

  def canvas_1_show (self, **event_args):
    # This method is called when the Canvas is shown on the screen
    self.w, self.h = drawing.CanvasObject.set_canvas(self.canvas_1)
    print('canvas: w={} h={}'.format(self.w, self.h))
    self.canvas_1.height = '{}px'.format(self.h)
    self.canvas_1.reset_context()

    # build arrays of clouds and stuff:
    self.buildings = []
    for i in range(24):
      self.buildings.append(drawing.RandomBuilding())
      
    self.clouds = []
    for i in range(8):
      self.clouds.append(drawing.RandomCloud())
      
    self.trees = []
    for tree in range(0):
      self.trees.append(drawing.RandomTree())
      
    self.far_trees = []
    for far_tree in range(12):
      self.far_trees.append(drawing.FarTree())
      
      