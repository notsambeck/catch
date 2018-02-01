import anvil.server
# import anvil.users
# import tables
# from tables import app_tables
import random


class ErrorHandler:
  def __init__(self, display_function):
    '''
    error handler that is called by an error, does display_function
    display_function could be Notification, alert, or print(python3)/future.print_function(python2.7)
    
    
    '''
    self.display_function = display_function
  
  def __call__(self, err):
    self.display_function(err)
    anvil.server.reset_session()
    me = anvil.server.call('start_session')
    if me:
      open_form('PlayScreen', me)
    else:
      open_form('LoginScreen')




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
