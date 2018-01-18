import anvil.secrets
import anvil.users
import tables
from tables import app_tables
import anvil.server

from utils import is_valid_number, hash_phone, generate_code
from twilio_auth import send_authorization_message

from datetime import datetime
import random

import bcrypt
from hashlib import blake2b


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
    return {'success': False,
            'enabled': False,
            'msg': 'invalid phone number',}

  user = app_tables.users.get(phone_hash=hash_phone(phone))

  if user:
    if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
      if user['enabled']:
        anvil.users.force_login(user)
        return {'success': True,
                'enabled': True,}
      else:
        return {'success': True,
                'enabled': False,}
    else:
      return {'success': False,
              'enabled': False,
              'msg': 'incorrect password',}
  else:
    return {'success': False, 
            'enabled': False,
            'msg': "account for {} does not exist".format(phone),}


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
  existing = app_tables.users.get(phone_hash=hash_phone(phone))  # account exists
  if existing:
    if not existing['dummy']:
      return {
        'success': False,
        'msg': 'user already exists',
      }
    
    else:  # existing is a dummy
      existing.update(
        dummy=False,
        enabled=False,
        handle=handle,
        password_hash=bhash(password),
        twilio_code=generate_code(),
        confirmations_sent=1,
      )

    return send_authorization_message(phone)
  
  else:    # number is valid and account does not exist
    user = app_tables.users.add_row(
      enabled=False,
      dummy=False,
      password_hash=bhash(password),
      phone_hash=hash_phone(phone),
      handle=handle,
      account_created=datetime.now(),
      confirmations_sent=1,
      twilio_code=generate_code(),
    )
    
    return send_authorization_message(phone)


@anvil.server.callable
def create_dummy(phone):
  '''
  Create a new dummy user from phone number
  Hashes phone number for storage.
  
  args: 
    phone: string

  returns:
    {success: True if success; False if user exists,
     msg: string explains status,
  '''
  assert isinstance(phone, str)

  phone = is_valid_number(phone)
  if not phone:                    # invalid number
    return {
      'success': False,
      'msg': 'invalid phone number'
    }
  if app_tables.users.get(phone_hash=hash_phone(phone)):  # account exists
    return {
      'success': False,
      'msg': 'user already exists'
    }
  
  else:                            # number is valid and account does not exist
    user = app_tables.users.add_row(
      enabled=False,
      dummy=True,
      phone_hash=hash_phone(phone),
      account_created=datetime.now(),
      confirmations_sent=0,
      twilio_code=generate_code(),
    )
    
    if user:
      return {'success': True,
              'msg': 'Confirmation not sent because, spam.'}
    
    else:
      return {'success': False,
              'msg': 'unknown failure in create_dummy'}


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
  # only works with logged in users
  if not anvil.users.get_user():
    return 
  
  u = app_tables.users.get(phone_hash=hash_phone(phone))  # needs to be called with keyword arg for table column name
  if u:
    return u.get_id()


@ anvil.server.callable
def confirm_account(code, phone):
  '''
  confirm a user has their twilio code

  changes user.enabled to True if success
  AND
  logs the user in
  
  args:
    user_id
    
  returns:
    bool: True or False
  '''
  user = app_tables.users.get(phone_hash=hash_phone(phone))
  
  if not user:
    return {'success': False,
            'msg': 'account does not exist',}
  
  elif user['enabled']:
    return {'success': False,
            'msg': 'account already verified, just log in',}
  
  if code == user['twilio_code']:
    user['enabled'] = True
    anvil.users.force_login(user)
    return {'success': True, 
            'msg': 'authed',}
  
  else:
    return {'success': False,
            'msg': 'code incorrect',}


@anvil.server.callable
def add_connection(phone):
  '''
  adds a connection to graph from current logged in to user with phone number
  
  args:
    other_user_id: user_id
    
  returns:
    {'success': bool,
     'enabled': bool,
     'msg': status,
     'game_id': game id ,}
  '''
  if not anvil.users.get_user():
    return {'success': False, 'msg': 'Not logged in.'}
  
  other_user = app_tables.users.get(phone_hash=hash_phone(phone))
  
  if other_user:
    print('try adding connection to', other_user['handle'])
    existing = [game for game in app_tables.graph.search() \
                if (game['player_1'] == other_user and game['player_2'] == anvil.users.get_user()) or \
                    (game['player_2'] == other_user and game['player_1'] == anvil.users.get_user())]
    if existing:
      return {'success': True,  # misleading
             'enabled': existing['player_2_enabled'],
             'msg': 'game already existed',
             'game_id': existing.get_id()}
    else:
      row = app_tables.graph.add_row(
        connection_time=datetime.now(),
        is_active=False,
        player_1=anvil.users.get_user(),
        player_2=other_user,
        player_2_enabled=other_user['enabled'])
      
      return {'success': True,
             'enabled': row['player_2_enabled'],
             'msg': 'game created',
             'game_id': row.get_id()}
  else:
    
    return {
      'success': False,
      'enabled': False,
      'msg': 'other player did not have an account',
      'game_id': None
           }
  

@anvil.server.callable
def get_connections():
  '''
  get all the connections with current user as p_1 or p_2
  '''
  user = anvil.users.get_user()
  
  if not user:
    return {'success': False, 'msg': 'Not logged in.'}
  
  # list all the games user is in.
  games = [game for game in app_tables.graph.search(tables.order_by('last_throw_time', ascending=False)) if game['player_1'] == user or game['player_2'] == user]

  return games


@anvil.server.callable
def make_game_active(connection_id):
  '''
  get the status of a game from perspective of logged in user; 
  start game if not already active.
  return game row or False'''
  game = app_tables.graph.get_by_id(connection_id)
  if not game['is_active']:
    with tables.Transaction() as txn:
      game['is_active'] = True
      game['who_has_ball'] = 1
      game['game_start_time'] = datetime.now()
      game['throws'] = 0
    print('set game', game['player_1']['handle'], 'vs', game['player_2']['handle'], '.is_active to:', game['is_active'])
  else:
    return {'success': False, 'msg': 'make_game_active: game is already active'}
  return {'success': True, 'game': game}


@anvil.server.callable
def throw(game_id):
  '''
  User pressed throw; 
  move ball pointer in database;
  return game row.
  '''
  print('throw called on {}'.format(game_id))
  game = app_tables.graph.get_by_id(game_id)
  
  if not game['is_active']:
    return {'success': False, 'msg': 'Must activate game before throwing.'}
  
  print(game['who_has_ball'], ' has the ball, who is: ', game['player_{}'.format(game['who_has_ball'])])
  print('versus this is user: ', anvil.users.get_user()) 

  with tables.Transaction() as txn:
    if game['player_1'] == anvil.users.get_user() and game['who_has_ball'] == 1:
      print('changing ball: 1 to 2')
      game['who_has_ball'] = 2
    elif game['player_2'] == anvil.users.get_user() and game['who_has_ball'] == 2:
      game['who_has_ball'] = 1
      print('changing ball: 2 to 1')
    else:
      print('returning failure')
      return {'success': False, 'msg': 'somehow you did not have the ball when you threw it'}

    print('recording throw / throw time')
    game['throws'] += 1
    game['last_throw_time'] = datetime.now()

  print('returning dict')
  return {'success': True, 'game': game}


@anvil.server.callable
def get_game_status(game_id):
  '''Get row for game_id'''
  return app_tables.graph.get_by_id(game_id)

'''
@anvil.server.callable
def some_connection():
  do_login('5555555555', '5')
  return get_connections().search()[0].get_id()
'''