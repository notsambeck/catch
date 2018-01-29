import random
import colors

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
    takes self (i.e. class) and a canvas; returns width, height'''
    cls._canvas = canvas
    cls._w = canvas.get_width()
    cls._h = canvas.get_height()
    print('canvas:', cls._canvas, cls._w, cls._h)
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
  def __init__(self, x, y, r, color='#fff'):
    '''
    draw a cirlce starting at x, y, 
    with radius r'''
    self.x = x
    self.y = y
    self.r = r
    self.color = color

  def draw(self):
    '''
    create rectangle, filled by default
    args:
      x, y, expressed as FLOATS 0.0 -> 1.0
      r, radius as % of width
      color
    ''' 
    CanvasObject._canvas.fill_style = self.color
    CanvasObject._canvas.begin_path()
    CanvasObject._canvas.arc(
      round((self.x +self.r) * CanvasObject._w), 
      round((self.y) * CanvasObject._h),
      round(self.r * CanvasObject._w),
      0, 6.3,   # TODO: this is probably supposed to be degrees?
    )
    CanvasObject._canvas.close_path()
    CanvasObject._canvas.fill()

   
class RandomBuilding(CanvasObject):
  def __init__(self):
    '''
    subclasses shape to have access to canvas.
    random building on wxh canvas
    '''
    bx = random.random()      # center
    bh = random.random() / 2  # top
    bw = random.choice([.01, .012, .03, .02, .023, .027, .025, .05, .07, .04])   # width
    self.l_side = Rectangle(bx - bw, bh, bw, CanvasObject._h, color=colors.building1)
    self.r_side = Rectangle(bx, bh, bw, CanvasObject._h, color=colors.building2)
    
  def draw(self):
    self.l_side.draw()
    self.r_side.draw()
    
    
class RandomCloud(CanvasObject):
  def __init__(self, size=24):
    '''
    subclasses shape to have access to canvas.
    random building on wxh canvas
    '''
    x = random.random()      # center
    y = random.random() / 2 - .2  # top
    self.parts = []
    for part in range(24):
      delta_x = random.random() / 15
      delta_y = random.random() / 15
      w = random.random() / 10 + .05
      h = random.random() / 10 + .05
      self.parts.append(Rectangle(x + delta_x, y - delta_y, 
                                  w, h, 
                                  color=random.choice([colors.cloud1,
                                                       colors.cloud2])))
    
  def draw(self):
    for part in self.parts:
      part.x -= .005
      if part.x < -.1:
        part.x = 1.1
      part.draw()