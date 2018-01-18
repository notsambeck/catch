import anvil.secrets
import anvil.users
import tables
from tables import app_tables
import anvil.server
from validators import is_valid_number

from datetime import datetime
import random

import twilio
import bcrypt

twilio_test_sid = 'AC8c06108afa619c6f98486555b0d09d8c'


def bhash(_string):
  '''returns: hash of string'''
  return bcrypt.hashpw(_string.encode('utf-8'), bcrypt.gensalt(12)).decode()


@anvil.server.callable
def do_login(phone, password):
  '''
  set anvil.session['user'] to user with this phone number if password hash matches
  
  args:
    phone: string: phone number
    password: string: of password
      
  returns:
    {
    success: bool
    msg: user_id string 
         OR 
         failure message
    }
  '''
  phone = is_valid_number(phone)
  if not phone:
    return {'success': False, 'msg': 'invalid phone number'}

  me = get_user_by_phone(phone)
  print(me, '= me')
  if me:
    if bhash(password) == me['password_hash']:
      anvil.users.force_login(me)
      return {'success': True, 'msg': anvil.users.get_user().get_id()}
    else:
      return {'success': False, 'msg': 'incorrect password'}
  else:
    return {'success': False, 'msg': "this account does not exist"}

 
@anvil.server.callable
def create_user(phone, password, handle):
  '''
  Create a new user 
  
  Requires pre-validated inputs

  Hashes password and phone number for storage.
  user_id is a generated primary key
  handle is string of user's display name
  
  args: 
    phone: string
    password: string
    handle: string

  returns:
    {
  success: True if success; False if user exists,
  msg: string explains status
    }
  '''
  assert isinstance(phone, str) and len(phone) == 10 and isinstance(handle, str)

  if get_user_by_phone(phone):
    return {
      'success': False,
      'msg': 'user already exists'
    }

  else:
    # TODO: enabled should be False until user confirms phone number (twilio); this is not set up yet
    
    rando = ''.join([str(random.randrange(10)) for _ in range(4)])

    me = app_tables.users.add_row(
      enabled=True,
      
      password_hash=bhash(password),
      phone_hash=bhash(phone),
      handle=handle,
      account_created=datetime.now(),
      confirmations_sent=0,
      twilio_code=rando,
    )

    return {'success': True, 'msg': rando}

def get_user_by_phone(phone):
  '''
  arg: 
    string: clean phone number
  
  returns:
    user_id for a phone number
    or
    None if it does not exist
    '''
  u = app_tables.users.get(phone_hash=bhash(phone))
  if u:
    return u.get_id()


@anvil.server.callable
def add_connection(other_user_id):
  '''adds a connection initiated by current user to other_user and vice versa.
  args:
    other_user_id: user_id  (obtain with check_user_exists
  internal: 
    other_user: row from user table
  '''
  other_user = app_tables.users.get_by_id(other_user_id)
  print('adding connection to', other_user['username'])
  row1 = app_tables.connections.add_row(game_ongoing=False,
                                        initiator=anvil.users.get_user(),
                                        recipient=other_user,)
  row2 = app_tables.connections.add_row(game_ongoing=False,
                                        initiator=other_user,
                                        recipient=anvil.users.get_user(),
                                        dual=row1,)
  row1['dual'] = row2
  return row1

  
@anvil.server.callable
def get_connections():
  '''get all the connections with current user as initiator as a client_readable table view'''
  me = anvil.users.get_user()
  if me:
    return app_tables.connections.search(initiator=me)


@anvil.server.callable
def make_game_active(connection_id):
  '''get the status of a connection from perspective of logged in user; 
  start game if not happening.
  return game row if I have ball, else False'''
  game = app_tables.connections.get_by_id(connection_id)
  if not game['game_ongoing']:
    with tables.Transaction() as txn:
      game['game_ongoing'] = True
      game['initiator_has_ball'] = True
      game['dual']['game_ongoing'] = True
      game['dual']['initiator_has_ball'] = False
    print('set game', game['initiator']['username'], 'vs', game['recipient']['username'], 'ongoing to:', game['game_ongoing'])
    print('set game', game['initiator']['username'], 'vs', game['recipient']['username'], 'p1 has ball to:', game['initiator_has_ball'])
    print('set game dual', game['dual']['initiator']['username'], 
          'vs', game['dual']['recipient']['username'], 
          'ongoing to:', game['dual']['game_ongoing'])
  else:
    print('internal: make_game_active: game is already active')
  return game


@anvil.server.callable
def throw(game_id):
  '''user pressed throw. Move ball pointer in both games'''
  game = app_tables.connections.get_by_id(game_id)
  game['initiator_has_ball'] = False
  game['dual']['initiator_has_ball'] = True
  game['dual']['updated'] = True
  return game


@anvil.server.callable
def check_update(game_id):
  '''Check whether game_id has been updated by other player.'''
  game = app_tables.connections.get_by_id(game_id)
  if game['updated']:
    game['updated'] = False
    return game
  else:
    return False

'''
@anvil.server.callable
def some_connection():
  do_login('5555555555', '5')
  return get_connections().search()[0].get_id()
'''