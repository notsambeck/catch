# import anvil.server
# import anvil.users
# import tables
# from tables import app_tables
import random

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
  # does not run in browser:
  '''
  h = blake2b(digest_size=30)
  h.update(phone.encode('utf-8'))
  return h.hexdigest()
  '''
  # does nothing:
  return phone


def generate_code(length=5):
  '''generate random string: numeric code of length __ (for Twilio)'''
  code = ''.join([str(random.randrange(0, 10)) for _ in range(length)])
  assert isinstance(code, str) and len(code) == length
  return code


def two_identical_game_iterators(games_1, games_2):
  '''
  returns true if games_1 == games_2
  else returns false
  '''
  if len(games_1) != len(games_2):
    return False
  
  for game in games_1:
    _id = game.get_id()
    other = games_2.get_by_id(_id)
    if game['throws'] != other['throws']:
      return False
  return True