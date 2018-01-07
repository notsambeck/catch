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
  '''take a phone number as a string, return an integer version if number is valid, else False'''
  print(number)
  
  number = [char for char in number if char not in '-_() ']
  for char in number:
    if char not in '0123456789':
      return None

  if len(number) != 10:
    return False

  else:
    return int(''.join(number))