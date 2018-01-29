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


def bhash(_string):
  '''
  returns: hash of _string;
  used for encrypting passwords only
  '''
  return bcrypt.hashpw(_string.encode('utf-8'), bcrypt.gensalt(12)).decode()


@anvil.server.callable
def has_stored_login():
  '''
  check for cookie with user id. encrypted, so this by itself is adequate security.
  if cookie exists, user is loged in.
  returns:
     True or False
  '''
  user = anvil.users.get_user(allow_remembered=True)
  if user:
    print('already logged in')
    return True
  else:
    print('not previously logged in')
  
  me = anvil.server.cookies.local.get('user')
  if me:
    print('cookie exists for {}'.format(me.get_id()))
    return me
  else:
    print('no login cookie stored')
    return False


@anvil.server.callable
def delete_cookie():
  print('cookie deleted')
  anvil.server.cookies.local.clear()

  
@anvil.server.callable
def do_login(phone, password, stay_logged_in):
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
            'msg': 'invalid phone number',}

  user = app_tables.users.get(phone_hash=hash_phone(phone))
  
  if user:
    if user['dummy']:
      return {'success': False,
              'msg': 'You need to create an account!',}

    # check password
    elif bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
      if user['enabled']:
        anvil.users.force_login(user, remember=stay_logged_in)

        return {'success': True,
                'enabled': True,
                'user': user,}
      else:
        return {'success': True,
                'enabled': False,
                'msg': 'user phone number not verified'}
      
    # not user
    else:
      return {'success': False,
              'enabled': False,
              'msg': 'incorrect password for this username',}
    
  # user doesn't exist
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
  if not phone:                    
    return {
      'success': False,
      'msg': 'invalid phone number'
    }
  existing = app_tables.users.get(phone_hash=hash_phone(phone))  
  
  # account exists and:
  if existing:
    
    # existing is a user-made account
    if not existing['dummy']:
      return {
        'success': False,
        'msg': 'user already exists',
      }
    
    # existing is a dummy
    else:
      existing.update(
        dummy=False,
        enabled=False,
        handle=handle,
        password_hash=bhash(password),
        twilio_code=generate_code(),
        confirmations_sent=0,)
  
  # OR:
  # account does not exist
  else:
    user = app_tables.users.add_row(
      enabled=False,
      dummy=False,
      password_hash=bhash(password),
      phone_hash=hash_phone(phone),
      handle=handle,
      account_created=datetime.now(),
      confirmations_sent=0,
      twilio_code=generate_code(),
    )
    
  # regardless of whether initializing new or dummy account, auth needed
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
      'msg': 'account already exists'
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
              'msg': 'Success, confirmation not sent because spam.'}
    
    else:
      return {'success': False,
              'msg': 'unknown failure in create_dummy'}


@anvil.server.callable
def get_user_id_by_phone(phone):
  '''
  Gets a user_id.
  Note that this function returns user_id, 
  however, anvil.users.get_user() returns ENTIRE ROW for current user.
  
  arg: 
    string: phone number
  
  returns:
    string: user_id
    or
    None: if user does not exist
    '''
  # only works for logged in user
  if not anvil.users.get_user():
    return {'success': False,
            'msg': 'not logged in'}
  
  u = app_tables.users.get(phone_hash=hash_phone(phone))  # needs to be called with keyword arg for table column name
  if u:
    return {'success': True,
            'user_id': u.get_id(),}
  else:
    return {'success': True,
            'msg': 'user does not exist',}


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
  me = app_tables.users.get(phone_hash=hash_phone(phone))
  
  if not me:
    return {'success': False,
            'goto_login': True,
            'msg': 'account does not exist, make one',}
  
  elif me['enabled']:
    return {'success': False,
            'goto_login': True,
            'msg': 'account already verified, just log in',}
  
  if code == me['twilio_code']:
    me['enabled'] = True
    anvil.users.force_login(me)
    
    # pre-activate games that dummy was in already
    existing_game_refs = app_tables.user_games.search(user=me)
    
    for row in existing_game_refs:
      row['game']['p1_enabled'] = True
      row['game']['throws'] = -1
  
    return {'success': True, 
            'msg': 'confirmed',}
  
  else:
    return {'success': False,
            'goto_login': False,
            'msg': 'code incorrect',}


@anvil.server.callable
def add_connection(phone):
  '''
  adds a connection to graph from current logged in to user with phone number
  user ('me') is player 0, other_user is player 1
  
  args:
    phone: other_user's phone number
    
  returns:
    {'success': bool,
     'enabled': bool,
     'msg': status description,
     'game': game (row reference),}
  '''
  me = anvil.users.get_user()
  if not me:
    return {
      'success': False,
      'msg': 'Not logged in.',}
  
  other_user = app_tables.users.get(phone_hash=hash_phone(phone))
  if not other_user:
    return {
      'success': False,
      'msg': 'other player did not have an account',}
  
  if other_user['handle']:
    # print('add connection to', other_user['handle'])
    pass
  else:
    pass
    # print('add hypothetical connection to {}'.format(phone))
    
  # protect whole operation from simultaneous adding
  with tables.Transaction() as txn:
    # search for pre-existing games

    my_games = app_tables.user_games.search(user=me)
    for row in my_games:
      if row['game']['player_1'] == other_user or row['game']['player_0'] == other_user:
        
        if row['game']['p1_enabled']:
          throws = -1
        else:
          throws = -2
        # success is not really 'True' but same result
        return {
          'success': True,
          'enabled': row['game']['p1_enabled'],
          'msg': 'game already exists',
          'game': row['game'],}
    
    # no existing connection; make one
    game = app_tables.games.add_row(
      connection_time=datetime.now(),
      is_active=False,
      player_0=me,
      player_1=other_user,
      p1_enabled=other_user['enabled'],
      throws=other_user['enabled'] - 2,
      last_throw_time=datetime.now(),)
    
    app_tables.user_games.add_row(game=game, user=me)
    app_tables.user_games.add_row(game=game, user=other_user)
      
    return {'success': True,
            'enabled': game['p1_enabled'],
            'msg': 'new game created',
            'game': game,}


@anvil.server.callable
def get_games():
  '''
  get all the connections for current user
  
  returns {'success': bool,
           'msg': status message,
           'order': list of game ids in order
           'games': {game_id: game},}
  '''
  me = anvil.users.get_user()
  
  if not me:
    return {'success': False, 
            'msg': 'Not logged in.'}
  
  else:
    games = {}
    order = []
    waiting = []
    for i, game in enumerate(app_tables.games.search(tables.order_by('throws', ascending=False))):
      if game['player_0'] == me or game['player_1'] == me:
        _id = game.get_id()
        if not game['p1_enabled']:
          waiting.append(_id)
        else:
          order.append(_id)
        games[_id] = game
    
    order += waiting
    assert len(order) == len(games)
    
    return {'success': True,
            'msg': 'retreived {} games'.format(len(games)),
            'order': order,
            'games': games,}


@anvil.server.callable
def make_game_active(game_id):
  '''
  get the status of a game; 
  start game if not already active;
  give activating user (me) the ball
  
  return game row or False
  '''
  
  game = app_tables.games.get_by_id(game_id)
  me = anvil.users.get_user()
  
  if game['player_0'] == me:
    has_ball = 0
  elif game['player_1'] == me:
    has_ball = 1
  else: 
    return {'success': False,
            'msg': 'you are not in this game',}

  if game['is_active']:
    return {'success': False,
            'msg': 'make_game_active: game is already active'}
      
  with tables.Transaction() as txn:
    game['is_active'] = True
    game['has_ball'] = has_ball
    game['game_start_time'] = datetime.now()
    game['throws'] = 0
  # print('set game', game['player_1']['handle'], 'vs', game['player_2']['handle'], '.is_active to:', game['is_active'])
  return {'success': True,
          'game': game}


@anvil.server.callable
def throw(game_id):
  '''
  User pressed throw; 
  move ball pointer in database;
  return game row.
  '''
  # print('throw() called at {}'.format(game_id))
  me = anvil.users.get_user()
  if not me:
    return {'success': False, 
            'msg': 'Not logged in.'}

  game = app_tables.games.get_by_id(game_id)
  if not game['is_active']:
    return {'success': False, 
            'msg': 'Must activate game before throwing.'}
  
  has_ball = 'player_{}'.format(game['has_ball'])
  # print(has_ball, ' has the ball now. name: ', game[has_ball]['handle'])

  if game[has_ball] != me:
    return {'success': False,
            'msg': 'you did not have the ball'}

  with tables.Transaction() as txn:

    game['has_ball'] = abs(1 - game['has_ball'])  # flip who has ball
    game['throws'] += 1
    game['last_throw_time'] = datetime.now()

  return {'success': True,
          'game': game}


@anvil.server.callable
def get_game(game_id):
  '''
  if user has permissions:
  returns game with id game_id 
  
  args: game id
  returns:
    {'success': bool,
     'game': game (row)}
  '''
  
  me = anvil.users.get_user()
  if not me:
    return {'success': False, 
            'msg': 'Not logged in.'}

  game = app_tables.games.get_by_id(game_id)
  
  if not (game['player_0'] == me or game['player_1'] == me):
    print('attempted to throw in someone elses game')
    return {'success': False, 
            'msg': 'You are not in that game.'}
  
  else:
    # print(game['has_ball'], ' has the ball')
    return {'success': True,
            'game': game}


@anvil.server.callable
def update_wall(number):
  me = anvil.users.get_user()
  if not me:
    return {'success': False, 
            'msg': 'Not logged in.'}
  
  me['wall_throws'] = number
  return {'success': True}

'''
@anvil.server.callable
def some_connection():
  do_login('5555555555', '5')
  return get_connections().search()[0].get_id()
'''