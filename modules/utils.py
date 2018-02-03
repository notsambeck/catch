import anvil.server
# import anvil.users
# import tables
# from tables import app_tables
import random


class ErrorHandler:
  def __init__(self, display_function, route_function, my_id=None):
    '''
    error handler that is called by an error, 
    does display_function
    routes using route_function
    
    display_function could be Notification, alert, or print(python3)/future.print_function(python2.7)
    route function should be open_form
    '''
    self.display_function = display_function
    self.route_function = route_function
    self.my_id = my_id
    self.debug = True
  
  def __call__(self, err):
    if self.display_function and self.debug:
      self.display_function('DEBUG MSG: Bumped from server. {}'.format(str(err)))
    if self.debug:
      print('reset_session()')
    anvil.server.reset_session()
    if self.debug:
      print('start_session({})'.format(str(self.my_id)))
    sess = anvil.server.call('start_session', self.my_id)
    if sess['success']:
      if self.debug:
        print(sess['msg'])
      self.route_function('PlayScreen', user=sess['user'])
    else:
      print('fail: {}'.format(sess['msg']))
      self.route_function('LoginScreen')


def is_valid_number(number):
  '''
  Args:
    string: phone number as a string
  
  returns
    string: cleaned number is valid, 
    or None
  '''
  # print('input number string to validate: ', number)
  
  number = [char for char in number if char not in '-_() .']
  for char in number:
    if char not in '0123456789':
      return None

  if len(number) != 10:
    return None

  else:
    return ''.join(number)
  

def hash_phone(phone):
  '''
  one-way but REPEATABLE hash for phone numbers.
  
  args: 
    string: numeric phone number;
 
  returns:
    string: static hash
  '''
  # this does not run in browser:
  '''
  h = blake2b(digest_size=30)
  h.update(phone.encode('utf-8'))
  return h.hexdigest()
  '''
  # so this does nothing:
  return phone


def generate_code(length=5):
  '''generate random string: numeric code of length __ (for Twilio)'''
  code = ''.join([str(random.randrange(0, 10)) for _ in range(length)])
  assert isinstance(code, str) and len(code) == length
  return code


def is_valid_color(string):
  '''
  check if a string is a valid color
  if valid:
    returns clean string of color
  else:
    returns False
  '''
  string = string.strip('''# '"''').lower()
  if not (len(string) == 3 or len(string) == 6):
    return False
  for char in string:
    if char not in '1234567890abcdef':
      return False
  return string


def rando(lo=0, hi=1):
  '''
  create a pseudorandom float between lo and hi
  '''
  assert hi > lo
  f = random.random()
  # scale
  f = f * (hi - lo)
  # push bottom edge of range to lo
  f += lo
  return f
