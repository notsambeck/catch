from anvil import *
import anvil.server
import anvil.users
import random
import drawing
from utils import rando
import datetime

hr = datetime.datetime.now().hour
# print('hour:', hr)

if hr < 6 or hr > 18:
  import colors_night as colors
elif 7 < hr < 17:
  import colors_day as colors
else:
  import colors_dusk as colors


from utils import ErrorHandler
error_handler = ErrorHandler(alert, open_form)

# TODO: remove the related code from web_callable before deployment
# as it may be a minor security issue
# random_id = anvil.server.call('some_connection')

# city

class PlayCatch (PlayCatchTemplate):
  def __init__(self, game, me, wrapper, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)
    
    set_default_error_handling(error_handler)
    
    self.me = me             # user row (dictionary-like)
    self.game = game         # Game (dictionary-like)
    self.wrapper = wrapper   # GameListElement that holds this game
    
    if game != 'wall' and game != 'robot':
      if not self.game['is_active']:
        activate = anvil.server.call_s('make_game_active', self.game.get_id())
        assert activate['success']
        self.game = activate['game']

      self.am0 = self.game['player_0'] == self.me
      
    if game == 'robot':
      self.am0 = True
      self.i_have_ball = True
      self.robot_counter = 0
    
    # motion loop counter
    self.counter = 0
    self.apple_counter = 0

    self.set_labels()
    self.set_directions()
    
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
      if self.game != 'robot':
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
    self.my_color_1 = self.wrapper.my_color_1
    self.my_color_2 = self.wrapper.my_color_2
    # print('PlayCatch', self.my_color_1)
    
    if self.game == 'wall':
      return True
    
    if self.game == 'robot':
      self.p1_name = 'Robot'
      self.opp_color_1 = colors.building1
      self.opp_color_2 = colors.building2
      return True
    
    self.p1_name = self.wrapper.you
    self.opp_color_1 = self.wrapper.opp_color_1
    self.opp_color_2 = self.wrapper.opp_color_2

  def throw_button_click(self, **event_args):
    if self.game == 'wall':
      return self.throw_wall()

    if not self.i_have_ball or self.ball_moving:
      return False
    
    if self.game == 'robot':
      return self.throw_robot()    
    
    # update local game state so slow server doesn't break this
    self.game['has_ball'] = 1 - self.game['has_ball']
    
    # reset y velocity
    self.ball_y = .78
    self.ball_vy = .06
    
    # change ball status so it starts moving
    self.ball_moving = True
    self.ball_steps = 0

    # tell server that ball has been thrown
    throw_status = anvil.server.call_s('throw', self.game.get_id())
    
    if not throw_status['success']:
      print('Throw failed:', throw_status['msg'])
      return False
    
    else:
      self.game = throw_status['game']
      self.wrapper.update(throw_status['game'])

  def throw_robot(self):
    if self.ball_moving:
      return False
    
    self.i_have_ball = not self.i_have_ball
    
    get_open_form().robot_throws += 1    # PlayScreen.wall_throws stays updated
    
    # reset y velocity
    self.ball_y = .78
    self.ball_vy = .06
    
    # change ball status so it starts moving
    self.ball_moving = True
    self.ball_steps = 0
    
    self.robot_counter += 1
    
  def throw_wall(self):
    if self.ball_moving:
      return False
    
    get_open_form().wall_throws += 1    # PlayScreen.wall_throws stays updated
    
    # reset y velocity
    self.ball_y = .78
    self.ball_vy = .06
    
    # change ball status so it starts moving
    self.ball_moving = True
    self.ball_steps = 0
    
    self.apple_counter += 1

  def ball_arrived(self):
    self.ball_steps = 0
    self.counter = 0
    self.ball_moving = False
    self.set_directions()
    
    if self.game == 'robot' and not self.i_have_ball:
      self.throw_robot()
      
  def draw(self, **event_args):
    '''
    this method runs every clock tick (timer element on Design view)
    '''
    
    if not self.canvas_1.visible:
      return
    
    self.canvas_1.reset_context()

    # alias
    c = self.canvas_1
    c.background = colors.sky
    
    self.counter += 1
    self.counter = self.counter % 500
    
    # clear the sky i.e. old clouds
    c.clear_rect(0, 0, self.w * 1.5, self.h * .65)
    
    # sun
    sun_height = (((hr % 12)-6)**2 - 15) * -.02
    # print(sun_height)
    drawing.Circle(0.8, sun_height, 0.02, colors.sun).draw()
    
    for cloud in self.clouds:
      cloud.draw()
    
    for bld in self.buildings:
      bld.draw()
    
    # ground
    drawing.Rectangle(0, .6, 1.5, .5, colors.grass).draw()

    for tree in self.far_trees:
      tree.draw()
    
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
      if self.game == 'robot':
        drawing.Rectangle(.9, .57, .08, .3, self.opp_color_1).draw()
        drawing.Rectangle(.9, .57, .08, .1, self.opp_color_2).draw()
        drawing.Rectangle(.87, .79, .04, .06, self.opp_color_2).draw()
      else:
        drawing.Rectangle(.9, .57, .04, .3, self.opp_color_1).draw()
        drawing.Circle(.88, .57, .035, self.opp_color_2).draw()
        drawing.Circle(.88, .79, .025, self.opp_color_2).draw()
    
    # wall: 
    if self.game == 'wall':
      # wall
      for delta in [.01 * i for i in range(8)]:
        drawing.Rectangle(.48 + delta, .36 + delta / 2, .03, .46 + delta / 2, colors.red).draw()   
      # end of wall
      drawing.Rectangle(.56, .4, .03, .5, colors.darkred).draw()
      
      if self.apple_counter == 2 and self.ball_steps == 6:
        print('launch apple')
        self.tree.apple_falling = True

      self.tree.draw()
    
    c.fill_style = colors.white
    
    # ball:
    ball_r = .017
    ball = drawing.Circle(self.ball_x, self.ball_y, ball_r).draw()
    
    if not self.ball_moving and (self.game == 'wall' or (self.game != 'wall' and self.i_have_ball)):
      for i in range(self.counter % 4):
        ball = drawing.Circle(self.ball_x - .002 * i, self.ball_y - .001 * i, ball_r + i * .002, filled=False).draw()

    # text:
    c.font = '{}px sans-serif'.format(self.h//12)
    pad = 9

    # wall text
    if self.game == 'wall':
      throws = get_open_form().wall_throws
      c.text_align = 'left'
      c.text_baseline = 'top'
      c.fill_text('THROWS: {}'.format(throws), pad, pad)
      c.fill_text('WALL RANK: {}'.format(self.me['wall_rank']), pad, pad + self.h // 11)
      c.text_align = 'center'
      c.text_baseline = 'bottom'
      if throws < 3 and self.counter % 5:
        c.fill_text('TAP TO THROW', c.get_width() // 2, self.h - pad)
        
    elif self.game == 'robot':
      throws = get_open_form().robot_throws
      c.text_align = 'left'
      c.text_baseline = 'top'
      c.fill_text('THROWS: {}'.format(throws), pad, pad)
      c.fill_text('ROBOT RANK: {}'.format(self.me['wall_rank']), pad, pad + self.h // 11)
      c.text_align = 'center'
      c.text_baseline = 'bottom'
      if throws < 2 and self.counter % 5:
        c.fill_text('TAP TO THROW', c.get_width() // 2, self.h - pad)

    else:
      c.text_align = 'right'
      c.text_baseline = 'bottom'
      c.fill_text(self.p1_name, self.w - pad * 4, self.h - pad)
      c.text_align = 'left'
      c.fill_text('Me', pad, self.h - pad)
      c.text_baseline = 'top'
      c.fill_text('THROWS: {}'.format(self.game['throws']), pad, pad)
      c.fill_text('GAME RANK: {}'.format(self.game['game_rank']), pad, pad + self.h // 11)
      if self.i_have_ball and self.game['throws'] <= 4 and not self.ball_moving and self.counter % 5:
        c.text_align = 'center'
        c.text_baseline = 'bottom'
        c.fill_text('TAP TO THROW', self.w // 2, self.h - pad)
    
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

  def update(self, updated_game):
    # update from server fed by game_list_element
    if self.game != 'wall' and not self.ball_moving:
      if updated_game['has_ball'] != self.game['has_ball']:
        # print('updating from server...')
        self.game = updated_game
        self.ball_moving = True
        self.ball_steps = 0
        self.ball_vy = .06

  def canvas_1_show (self, **event_args):
    # This method is called when the Canvas is shown on the screen
    self.w, self.h = drawing.CanvasObject.set_canvas(self.canvas_1)
    if self.game == 'wall':
      print('canvas for wall: {} x {}'.format(self.w, self.h))
    # print('canvas: w={} h={}'.format(self.w, self.h))
    self.canvas_1.height = '{}px'.format(self.h)
    self.canvas_1.reset_context()

    # build arrays of clouds and stuff:
    self.buildings = []
    for i in range(24):
      self.buildings.append(drawing.RandomBuilding())
      
    self.clouds = []
    for i in range(8):
      self.clouds.append(drawing.RandomCloud())
     
    if self.game == 'wall':
      self.tree = drawing.BigTree()
          
    self.far_trees = []
    for far_tree in range(12):
      self.far_trees.append(drawing.FarTree())
      
      