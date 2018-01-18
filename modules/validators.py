# import anvil.server
# import anvil.users
# import tables
# from tables import app_tables

# This is a module.
# You can define variables and functions here, and use them from any form. For example:
#
#    import Module1
#
#    Module1.say_hello()
#

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
  # one option:
  
  '''
  h = blake2b(digest_size=30)
  h.update(phone.encode('utf-8'))
  return h.hexdigest()
  '''
  
  # alternatively:
  return phone
