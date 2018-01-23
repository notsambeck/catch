from anvil import *
import anvil.server
import anvil.users

# TODO following function call and definition in ServerModule for deployment?
# random_id = anvil.server.call('some_connection')

class PlayWall(PlayWallTemplate):
  def __init__(self, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)
    
    self.me = anvil.users.get_user()
    
    self.throws = self.me['wall_throws']
    
    self.counter = 0

    self.set_labels_directions()
      
  def set_labels_directions(self):
    # set movement vairables
    self.ball_moving = False
    
    self.ball_x = .12
    self.ball_vx = .04
    
    # set y / y_velocity
    self.ball_y = .76
    self.ball_vy = .06
 
  def throw_button_click(self, **event_args):
    if self.ball_moving:
      return False
    self.throws += 1
    if self.throws % 10 == 0:
      anvil.server.call_s('update_wall', self.throws)

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
    c.fill_style = "rgba(200,200,200,.2)"
    for cloud in ((100, 20, 4, 0), (77, 45, 5, 30), (30, 120, 5, 40), (50, 120, 4, 63), (188, 103, 8, 90),
                 (100, 60, 2, 0), (230, 405, 5, 10), (70, 200, 3, 70), (160, 60, 7, 23), (218, 39, 2, 60),
                 (100, 60, 2, 80), (230, 405, 5, 50), (70, 200, 3, 40), (160, 60, 7, 53), (218, 39, 2, 95)):
      x = (cloud[3] - self.counter) * w // 300
      if x < 0:
        x += w
      c.fill_rect(x, h // cloud[2], cloud[0], cloud[1])
      
    c.fill_style = "rgba(180,180,180,.15)"
    for cloud in ((100, 20, 4, 0), (77, 45, 5, 30), (30, 120, 5, 40), (50, 120, 4, 63), (188, 103, 8, 90),
                 (100, 60, 2, 0), (230, 405, 5, 10), (70, 200, 3, 70), (160, 60, 7, 23), (218, 39, 2, 60),
                 (100, 60, 2, 80), (230, 405, 5, 50), (70, 200, 3, 40), (160, 60, 7, 53), (218, 39, 2, 95)):
      x = (cloud[3] - self.counter) * w // 250
      if x < -100:
        x += w
      c.fill_rect(x, h/2 // cloud[2], cloud[0], cloud[1])
      
    # city
    c.fill_style = "rgba(100,100,100,1)"
    c.fill_rect(300, h/3, w//18, h//2)
    c.fill_rect(220, .35*h, w//20, 2*h//3)
    c.fill_rect(320, .25*h, w//50, h//2.2)
    c.fill_rect(400, .5*h, w//15, h//1.6)
    c.fill_rect(490, .35*h, w//26, 2*h//3.7,)
    c.fill_rect(650, .25*h, w//40, h//2.7,)
    c.fill_rect(200, h/3, w//30, h//2.1)
    c.fill_rect(520, .35*h, w//20, 3*h//5)
    c.fill_rect(620, .25*h, w//40, h//2)
    c.fill_rect(700, .5*h, w//45, h//3)
    c.fill_rect(190, .35*h, w//32, 2*h//3.2,)
    c.fill_rect(50, .25*h, w//30, h//2.6,)
    
    c.fill_style = "rgba(60,60,90,1)"
    c.fill_rect(330, h/3, w//18, h//2)
    c.fill_rect(260, .35*h, w//20, 2*h//3)
    c.fill_rect(330, .25*h, w//50, h//2.2)
    c.fill_rect(440, .5*h, w//15, h//1.6)
    c.fill_rect(520, .35*h, w//26, 2*h//3.7,)
    c.fill_rect(670, .25*h, w//40, h//2.7,)
    c.fill_rect(230, h/3, w//30, h//2.1)
    c.fill_rect(560, .35*h, w//20, 3*h//5)
    c.fill_rect(630, .25*h, w//40, h//2)
    c.fill_rect(720, .5*h, w//45, h//3)
    c.fill_rect(210, .35*h, w//32, 2*h//3.2,)
    c.fill_rect(80, .25*h, w//30, h//2.6,)
    
    # trees
    c.fill_style = "rgba(100,110,70,1)"
    c.fill_rect(0, .6*h, (w*1.2)//1, h//2)
    
    # ground
    c.fill_style = "rgba(100,120,80,1)"
    c.fill_rect(0, h*2//3, (w*1.2)//1, h//3)
    
    # players
    c.fill_style = "rgba(0,0,0,1)"
    c.fill_rect(.1*w, .65*h, .04*w, .25*h )
    c.fill_style = '#AA9900'
    # heads
    c.fill_rect(.1*w, .59*h, .04*w, .08*h )
    # gloves
    c.fill_rect(.12*w, .75*h, .03*w, .06*h )
    
    # wall
    c.fill_style = '#883300'
    c.fill_rect(w*.52, h*.27, w//40, h*2//3)
    c.fill_rect(w*.51, h*.26, w//40, h*2//3)
    c.fill_rect(w*.50, h*.25, w//40, h*2//3)
    c.fill_rect(w*.49, h*.24, w//40, h*2//3)
    c.fill_rect(w*.48, h*.23, w//40, h*2//3)
    c.fill_rect(w*.47, h*.22, w//40, h*2//3)
    c.fill_style = '#702000'
    c.fill_rect(w*.53, h*.28, w//40, h*2//3)

    
    c.fill_style = '#FFFFFF'
    c.font = '{}px sans-serif'.format(h//9)
    
    c.fill_text('THROWS:'.format(self.throws), (w*.6), h//2)
    c.fill_text('{}'.format(self.throws), w*.6, h*.8)
    if not self.ball_moving and self.counter % 5:
      c.fill_text('TAP TO THROW', w//16, h//6)
    
    # ball:
    c.fill_style = '#FEF5E7'
    c.fill_rect(self.ball_x * w, self.ball_y * h, .024*w, .05*h )
    
    if self.ball_moving:
      self.ball_steps += 1
      
      # direction
      if self.ball_steps < 10:
        self.ball_x += self.ball_vx
      else:
        self.ball_x -= self.ball_vx
        
      self.ball_y -= self.ball_vy   # indexed from top
      self.ball_vy -= .007
      
      if self.ball_steps == 19:
        # print('ball has arrived')
        self.ball_arrived()
        