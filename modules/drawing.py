import random
import colors
from utils import rando

'''
html5 canvas drawing methods, for use in PlayCatch (and subclasses)
'''
class CanvasObject:
  _canvas = None
  _w = None
  _h = None
  
  # this warning is incorrect i think
  @classmethod
  def set_canvas(cls, canvas):
    '''
    takes self (i.e. class) and a canvas; returns width, height
    '''
    cls._canvas = canvas
    cls._w = min(int(canvas.get_width()), 900)
    cls._canvas.height = '{}px'.format(cls._w // 1.4)
    cls._h = canvas.get_height()
    print('canvas set:', cls._canvas, cls._w, cls._h)
    return cls._w, cls._h
  
  def draw(self):
    # must be subclassed
    raise ShapeError('draw not defined for abstract CanvasObject')


class Rectangle(CanvasObject):
  def __init__(self, x, y, w, h, color='#aaa'):
    '''
    create rectangle, filled by default
    args:
      x, y,
      w, h, expressed as FLOATS 0.0 -> 1.0
      color
    '''
    self.x = x
    self.y = y
    self.w = w
    self.h = h
    self.color = color

  def draw(self):
    '''draws filled rectangle'''
    CanvasObject._canvas.fill_style = self.color
    CanvasObject._canvas.fill_rect(
      round(self.x * CanvasObject._w), 
      round(self.y * CanvasObject._h),
      round(self.w * CanvasObject._w),
      round(self.h * CanvasObject._h),
    )
    
    
class Circle(CanvasObject):
  def __init__(self, x, y, r, color='#fff', filled=True):
    '''
    draw a cirlce starting at x, y, 
    with radius r'''
    self.x = x
    self.y = y
    self.r = r
    self.color = color
    self.filled = filled

  def draw(self):
    '''
    create circle, filled by default
    args:
      x, y, at center; expressed as FLOATS 0.0 -> 1.0
      r, radius as % of width
      color
    ''' 
    CanvasObject._canvas.begin_path()
    CanvasObject._canvas.arc(
      round((self.x + self.r) * CanvasObject._w), 
      round((self.y + self.r) * CanvasObject._h),
      round(self.r * CanvasObject._w),
      0, 6.3,   # TODO: this is probably supposed to be degrees?
    )
    CanvasObject._canvas.close_path()
    if self.filled:
      CanvasObject._canvas.fill_style = self.color
      CanvasObject._canvas.fill()
    else:
      CanvasObject._canvas.stroke_style = self.color
      CanvasObject._canvas.stroke()
   
class RandomBuilding(CanvasObject):
  def __init__(self):
    '''
    subclasses shape to have access to canvas.
    random building on wxh canvas
    '''
    bx = random.random()      # center
    bh = rando(0.1, 0.35)  # top
    bw = random.choice([.015, .012, .03, .02, .023, .027, .025, .05, .07, .04])   # width
    self.l_side = Rectangle(bx - bw, bh + .2, bw, CanvasObject._h, color=colors.building1)
    self.r_side = Rectangle(bx - .002, bh + .2, bw, CanvasObject._h, color=colors.building2)
    
  def draw(self):
    self.l_side.draw()
    self.r_side.draw()
    
    
class RandomCloud(CanvasObject):
  def __init__(self, size=8):
    '''
    subclasses shape to have access to canvas.
    random building on wxh canvas
    '''
    self.velocity = rando(.003, .006)
    x = random.random()      # center
    y = rando(-0.1, 0.3)  # top
    self.parts = []
    for part in range(size):
      delta_x = rando(0, 0.06)
      delta_y = rando(0, 0.06)
      w = rando(0.03, 0.2)
      h = rando(0.05, 0.15)
      self.parts.append(Rectangle(x + delta_x, y - delta_y, 
                                  w, h, 
                                  color=random.choice([colors.cloud1,
                                                       colors.cloud2])))
    
  def draw(self):
    for part in self.parts:
      part.x -= self.velocity
      if part.x < -.1:
        part.x = 1.1
      part.draw()
      
class FarTree(CanvasObject):
  def __init__(self):
    '''
    subclasses shape to have access to canvas.
    random tree on w*h canvas
    '''
    x = random.random()      # center
    y = .53 + rando(-.03, .03)
    delta = rando(-.01, .01)
    h = .13 + delta
    r = .03 + delta
    w = .01
    self.trunk = Rectangle(x + r - w/2, y, w, h, colors.darkred)

    self.leaf = Circle(x,
                       y,
                       r,
                       colors.leaf2)
  def draw(self):
    self.trunk.draw()
    self.leaf.draw()
      
      
class RandomTree(CanvasObject):
  wind = 0
  def __init__(self, size=64):
    '''
    subclasses shape to have access to canvas.
    random tree on w*h canvas
    '''
    x = rando(.1, .9)   # center
    y = .55
    self.leaves = []
    self.trunk = Rectangle(x + .03, y, .02, .18, colors.darkred)
    for part in range(size):
      delta_x = random.random() * .06
      delta_y = random.random() * .06
      r = .01
      self.leaves.append(Circle(x + delta_x,
                                y - 1.8 * delta_y,
                                r,
                                color=random.choice([
                                  colors.leaf1,
                                  colors.leaf2,
                                  colors.leaf3,
                                  colors.leaf4,
                                  colors.leaf5,
                                ])))
    
  def draw(self):
    self.trunk.draw()
    for leaf in self.leaves:
      angle = random.random()
      if angle > self.wind:
        leaf.draw()
  
  @classmethod
  def update_wind(self):
    inc = rando(-.02, .02)
    if self.wind > .2:
      self.wind = .2
    elif self.wind < 0.0:
      self.wind = 0.0
