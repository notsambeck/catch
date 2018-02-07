import anvil.secrets
import anvil.users
import tables
from tables import app_tables
import anvil.server

from utils import is_valid_number, hash_phone, generate_code
from twilio_auth import send_authorization_message

from datetime import datetime
from game_management import get_games

import bcrypt

debug = True


def bhash(_string):
  '''
  returns: hash of _string;
  used for encrypting passwords only
  '''
  return bcrypt.hashpw(_string.encode('utf-8'), bcrypt.gensalt(12)).decode()


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
  me = anvil.server.session.get('me', False)
  if not me:
    return {
      'success': False,
      'msg': 'not logged in',
    }
  
  other_user = app_tables.users.get(phone_hash=hash_phone(phone))
  if not other_user:
    return {
      'success': False,
      'msg': 'other player did not have an account',
    }
  
  if other_user['handle']:
    # print('add connection to', other_user['handle'])
    pass
  else:
    pass
    # print('add hypothetical connection to {}'.format(phone))
    
  my_games = get_games(server=True)  # get a dict of games by id

  # protect whole operation from simultaneous adding
  with tables.Transaction() as txn:
    # search for pre-existing games
    
    for _id, game in my_games.items():
      if game['player_1'] == other_user or game['player_0'] == other_user:
        
        # this used to return True.
        return {
          'success': False,
          'enabled': game['p1_enabled'],
          'msg': 'game already exists',
          'game': game,}
  
    # no existing connection; make one
    game = app_tables.games.add_row(
      connection_time=datetime.utcnow(),
      is_active=False,
      player_0=me,
      player_1=other_user,
      p1_enabled=other_user['enabled'],
      throws=other_user['enabled'] - 2,
      last_throw_time=datetime.utcnow(),)
            
    return {'success': True,
            'enabled': game['p1_enabled'],
            'msg': 'new game created',
            'game': game,}

# insecure login from stored user id:
  '''
  if debug:
    print('my_id passed by browser: {}'.format(str(my_id)))
  if my_id:
    me = app_tables.users.get_by_id(my_id)
    if debug:
      print('new session from browser')
      print('would cookie have worked?')
      print(anvil.server.cookies.local.get("user_id", False))
      try:
        cookie_id = anvil.server.cookies.local['user_id']
        print('method2: {}'.format(cookie_id))
      except:
        print('user_id not found (errored)')
    row_login(me, True)
        
    return {'success': True,
            'user': me,
            'msg': 'new session - browser remembered id',}
  '''

@anvil.server.callable
def start_session():
  '''
  start a new session for returning user.
  
  args: 
    None

  Tries:
    Existing session
    Remembered user
    Other cookie
    Fail
  
  does:
    force_login()
    stores user info in memory at anvil.server.session['me']
    makes a cookie
    
  returns:
     {'success': bool,
     'user': user row if success,
     'msg': status msg,}
  '''
  if debug:
    print('start_session...')
  
  me = anvil.server.session.get('me', False)
  if debug:
    print('me stored in anvil.server.session: {}'.format(str(me)))
  if me:
    row_login(me, anvil.server.session['remember_me'])
    if debug:
      print('restarting current session')
        
    return {'success': True,
            'user': me,
            'msg': 'restart existing session',}
 
  # not live session; is there a cookie?
  # if so log back in and remember.
  my_id = anvil.server.cookies.local.get('user_id', False)
  if debug:
    print('get cookie - user_id: {}'.format(str(my_id)))
    
  if my_id:
    # clear cookie and make new one
    me = app_tables.users.get_by_id(my_id)
    row_login(me, remember_me=True, cookie_supplied=True)
    return {'success': True,
            'user': me,
            'msg': 'cookie found, logging in'}
  
  if debug:
    print('automatic login failed')
  # anvil.server.cookies.local.clear()  
  return {'success': False,
          'msg': 'no login information found, please log in',}


def row_login(user_row, remember_me, cookie_supplied=False):
  '''
  does the actions to start new session for a user row
  
  sets new 
  
  '''
  if debug:
    print('{}:\nrow_login(remember_me={})'.format(user_row['handle'], str(remember_me)))
    
  # forget user (we are only using cookie at this time)
  anvil.users.force_login(user_row, remember=False,)  
  
  anvil.server.session['me'] = user_row
  anvil.server.session['remember_me'] = remember_me

  if remember_me and not cookie_supplied:
    anvil.server.cookies.local.set(365, user_id=user_row.get_id())
    if False:
      print('wrote cookie, now reading: {}'.format(anvil.server.cookies.local.get("user_id", False)))
      
  app_tables.user_actions.add_row(user=user_row, action_type='login', time=datetime.utcnow())
  
  ### RANKING ###
  # TODO: fix this hack
  
  if user_row['phone_hash'] == '5555555555':
    start_time = datetime.utcnow()
    print('Fake User logged in. ranking...')
    generate_game_ranks()
    generate_wall_ranks()
    generate_robot_ranks()
    print('done. time={}'.format(datetime.utcnow() - start_time))
  
  return True


@anvil.server.callable
def do_logout():
  if debug:
    print('deleting cookie, session vars; logging out.')
  anvil.server.cookies.local.clear()
  anvil.users.logout()
  anvil.server.session['me'] = None
  anvil.server.session['remember_me'] = False
  if debug:
    print('cookie after logout(): {}'.format(anvil.server.cookies.local.get("user_id", False)))
    print('session vars after logout(): {}'.format(anvil.server.session['me']))

  
@anvil.server.callable
def do_login(phone, password, stay_logged_in):
  '''
  set anvil.session['user'] to user with this phone number if password hash matches
  stores user info in memory at anvil.server.session['me']
  
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
    # check it's a real user
    if user['dummy']:
      return {'success': False,
              'msg': 'You need to create an account!',}

    # check password
    elif bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
      if user['enabled']:
        row_login(user, stay_logged_in)
        return {'success': True,
                'enabled': True,
                'user': user,
                'msg': 'stay_logged_in={}'.format(str(stay_logged_in)),}
      else:
        return {'success': True,
                'enabled': False,
                'msg': 'user phone number not verified'}
      
    else:
      return {'success': False,
              'enabled': False,
              'msg': 'incorrect password for this phone number',}
    
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
  Sends Twilio authorization message
  
  TODO: this function cannot be user authenticated - it's for new users.
  does it need to have a Captcha or something?
  
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
        'msg': 'user already exists, please log in',
      }
    
    # existing is a dummy
    else:
      existing.update(
        dummy=False,
        enabled=False,
        is_new=True,
        handle=handle,
        password_hash=bhash(password),
        twilio_code=generate_code(),
        confirmations_sent=0,
        wall_throws=0,
        robot_throws=0,)
  
  # OR:
  # account does not exist
  else:
    user = app_tables.users.add_row(
      enabled=False,
      is_new=True,
      dummy=False,
      password_hash=bhash(password),
      phone_hash=hash_phone(phone),
      handle=handle,
      account_created=datetime.utcnow(),
      confirmations_sent=0,
      wall_throws=0,
      robot_throws=0, 
      twilio_code=generate_code(),
    )
    
  # regardless of whether initializing new or dummy account, auth needed
  return send_authorization_message(phone)


@anvil.server.callable
def create_dummy(phone):
  '''
  Create a new dummy user from phone number
  AND
  connects logged in user to dummy if successful
  
  args: 
    phone: string

  returns:
    {success: True if success; False if user exists,
     msg: string explains status,
  '''
  me = anvil.server.session.get('me', False)
  if not me:
    return {
      'success': False,
      'msg': 'not logged in',
    }
  
  # USER ACTIONS LOG
  app_tables.user_actions.add_row(user=me, action_type='create_dummy', time=datetime.utcnow())
  
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
      account_created=datetime.utcnow(),
      confirmations_sent=0,
      twilio_code=generate_code(),
    )
    
    if user:
      return add_connection(phone)
    

    else:
      return {'success': False,
              'msg': 'unknown failure in create_dummy'}


@anvil.server.callable
def get_user_id_status_by_phone(phone):
  '''
  Gets a user_id by phone number
  
  Note that this function returns user_id, 
  however, anvil.users.get_user() returns ENTIRE ROW for current user.
  
  arg: 
    string: phone number
  
  returns:
    {'success': bool,
    'exists': bool,
    'enabled': bool,
    'msg': status message,
    'user_id': user_id if success}
    '''
  # only works for logged in user
  me = anvil.server.session.get('me', False)
  if not me:
    return {
      'success': False,
      'msg': 'not logged in',
    }
  
  u = app_tables.users.get(phone_hash=hash_phone(phone))  # needs to be called with keyword arg for table column name
  if u:
    return {'success': True,
            'exists': True,
            'enabled': u['enabled'],
            'user_id': u.get_id(),
           'msg': 'user exists',}
  else:
    return {'success': True,
            'exists': False,
            'enabled': False,
            'msg': 'user does not exist',}


@anvil.server.callable
def confirm_account(code, phone, remember_me):
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
    row_login(me, remember_me=remember_me)
    
    # pre-activate games that dummy was in already
    existing_games = app_tables.games.search(player_1=me)
    
    for game in existing_games:
      game['p1_enabled'] = True
      game['throws'] = -1
      
    # USER ACTIONS LOG
    app_tables.user_actions.add_row(user=me, action_type='confirm_account', time=datetime.utcnow())
  
    return {'success': True, 
            'msg': 'confirmed',
            'goto_login': False,
            'user': me,}
  
  else:
    return {'success': False,
            'goto_login': False,
            'msg': 'code incorrect',}

  
def generate_game_ranks():
  for i, game in enumerate(app_tables.games.search(tables.order_by('throws', ascending=False))):
    game['game_rank'] = i+1

def generate_wall_ranks():
  for i, user in enumerate(app_tables.users.search(tables.order_by('wall_throws', ascending=False))):
    user['wall_rank'] = i+1
    
def generate_robot_ranks():
  for i, user in enumerate(app_tables.users.search(tables.order_by('robot_throws', ascending=False))):
    user['robot_rank'] = i+1