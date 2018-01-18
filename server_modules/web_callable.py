import anvil.secrets
import anvil.users
import tables
from tables import app_tables
import anvil.server
from validators import is_valid_number, hash_phone

from datetime import datetime
import random

import twilio
import bcrypt
from hashlib import blake2b


twilio_test_sid = 'AC8c06108afa619c6f98486555b0d09d8c'


def bhash(_string):
  '''
  returns: hash of _string;
  used for encrypting passwords only
  '''
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

  user_id = get_user_id_by_phone(phone)
  user = app_tables.users.get_by_id(user_id)

  if user:
    if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
      anvil.users.force_login(user)
      return {'success': True,
              'user_id': user_id,
              'user_enabled': user['enabled']}
    else:
      return {'success': False, 'msg': 'incorrect password'}
  else:
    return {'success': False, 'msg': "account {} does not exist".format(phone)}

 
@anvil.server.callable
def create_user(phone, password, handle):
  '''
  Create a new user from pre-validated inputs
  Hashes password and phone number for storage.
  
  args: 
    phone: string
    password: string
    handle: string

  returns:
    {success: True if success; False if user exists,
     msg: string explains status,
     --optional-- user_id: user_id}
  '''
  assert isinstance(phone, str) and isinstance(handle, str)

  phone = is_valid_number(phone)
  if not phone:                    # invalid number
    return {
      'success': False,
      'msg': 'invalid phone number'
    }
  if get_user_id_by_phone(phone):  # account exists
    return {
      'success': False,
      'msg': 'user already exists'
    }
  
  else:                            # number is valid and account does not exist
    # TODO: enabled should be False until user confirms phone number (twilio)
    rando = ''.join([str(random.randrange(10)) for _ in range(4)])
    

    user = app_tables.users.add_row(
      enabled=False,
      password_hash=bhash(password),
      phone_hash=hash_phone(phone),
      handle=handle,
      account_created=datetime.now(),
      confirmations_sent=0,
      twilio_code=rando,
    )

    if not user:
      # in case of insertion error
      raise InsertionError(phone)
    
    return {
       'success': True,
      'twilio_code': rando,           # TODO: this is fake!
      'user_id': user.get_id(),
    }


@anvil.server.callable
def get_user_id_by_phone(phone):
  '''
  Gets a user_id.
  Note that in contrast to this function wich returns user_id,
  anvil.users.get_user() returns ENTIRE ROW for current user.
  
  arg: 
    string: clean phone number
  
  returns:
    string: user_id
    or
    None: if user does not exist
    '''
  phone_hash=hash_phone(phone)
  u = app_tables.users.get(phone_hash=phone_hash)  # needs to be called with keyword arg for table column name
  if u:
    return u.get_id()


@ anvil.server.callable
def confirm_account(code, user_id):
  '''
  confirm a user has their twilio code
  changes user.enabled to True if success
  
  args:
    user_id
    
  returns:
    bool: True or False
  '''
  user = app_tables.users.get_by_id(user_id)
  if code == user['twilio_code']:
    user['enabled'] = True
    anvil.users.force_login(user)
    return True
  else:
    return False


@anvil.server.callable
def add_connection(other_user_id):
  '''
  adds a connection to graph from current logged in to user with phone number
  
  args:
    other_user_id: user_id
    
  returns:
    row: new connection
  '''
  other_user = app_tables.users.get_by_id(other_user_id)
  print('adding connection to', other_user['handle'])
  row = app_tables.graph.add_row(connection_time=datetime.now(),
                                 is_active=False,
                                 player_1=anvil.users.get_user(),
                                 player_2=other_user)
  return row

  
@anvil.server.callable
def get_connections():
  '''
  get all the connections with current user as p_1 or p_2
  '''
  user = anvil.users.get_user()
  
  if not user:
    return {'success': False, 'msg': 'Not logged in.'}
  
  user_id = user.get_id()
  
  if user_id:
    # list all the games user is in.
    games = [game for game in app_tables.graph.search() if game['player_1'] == user_id or game['player_2'] == user_id]
    
  return games
  
    

@anvil.server.callable
def make_game_active(connection_id):
  '''get the status of a connection from perspective of logged in user; 
  start game if not happening.
  return game row if I have ball, else False'''
  game = app_tables.graph.get_by_id(connection_id)
  if not game['is_active']:
    with tables.Transaction() as txn:
      game['is_active'] = True
      game['who_has_ball'] = 1
      game['game_start_time'] = datetime.now()
    print('set game', game['player_1']['handle'], 'vs', game['player_2']['handle'], 'ongoing to:', game['is_active'])
  else:
    print('internal: make_game_active: game is already active')
  return game


@anvil.server.callable
def throw(game_id):
  '''
  User pressed throw; 
  move ball pointer in database;
  return game row.
  '''
  game = app_tables.graph.get_by_id(game_id)
  
  if not game['is_active']:
    return {'success': False, 'msg': 'Game not active to make a throw.'}
  
  has_ball = game['who_has_ball']
  if game['player_{}'.format(str(has_ball))] == anvil.users.get_user().get_id():
    if has_ball == 1:
      game['who_has_ball'] == 2
    else:
      game['who_has_ball'] == 1
    game['throws'] = game['throws'] + 1
    game['last_throw_time'] = datetime.now()
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