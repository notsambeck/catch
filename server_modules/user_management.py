import anvil.secrets
import anvil.users
import tables
from tables import app_tables
import anvil.server

from utils import is_valid_number, hash_phone, generate_code
from twilio_auth import send_authorization_message

from datetime import datetime

import bcrypt

debug = True


def bhash(_string):
  '''
  returns: hash of _string;
  used for encrypting passwords only
  '''
  return bcrypt.hashpw(_string.encode('utf-8'), bcrypt.gensalt(12)).decode()


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
  me = anvil.server.session.get('me', False)
  if me:
    if row_login(me, anvil.server.session['remember']):
      return {'success': True,
              'user': me,
              'msg': 'already logged in',}
  
  me = anvil.users.get_user(allow_remembered=True)
  if me:
    if row_login(me, False):
      return {'success': True,
              'user': me,
              'msg': 'get user (remembered)'}
  
  # not remembered; is there another cookie? 
  # the same cookie system should have worked above?
  my_id = anvil.server.cookies.local.get('user_id', False)
  if my_id:
    print('force_login() failed but cookie exists for {}'.format(my_id))
    
    # clear cookie and make new (so format could be changed in the future)
    anvil.server.cookies.local.clear()
    me = app_tables.users.get_by_id(my_id)
    if row_login(me, True):
      return {'success': True,
              'user': me,
              'msg': 'cookie found, logging in (WEIRD!)'}
  
  # in case of bad cookie:
  anvil.server.cookies.local.clear()
  return {'success': False,
          'msg': 'no login information found, go to login',}


def row_login(user_row, remember):
  '''
  does the actions to start new session for a user row
  '''
  if debug:
    print('row_login: user={} remember={}'.format(str(user_row), str(remember)))
  anvil.users.force_login(user_row, remember=remember)
  anvil.server.session['me'] = user_row
  anvil.server.session['remember'] = remember
  if remember:
    anvil.server.cookies.local.set(3650, user_id=user_row.get_id())
  return True


@anvil.server.callable
def delete_cookie():
  if debug:
    print('cookie deleted')
  anvil.server.cookies.local.clear()

  
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
        handle=handle,
        password_hash=bhash(password),
        twilio_code=generate_code(),
        confirmations_sent=0,
        wall_throws=0,)
  
  # OR:
  # account does not exist
  else:
    user = app_tables.users.add_row(
      enabled=False,
      dummy=False,
      password_hash=bhash(password),
      phone_hash=hash_phone(phone),
      handle=handle,
      account_created=datetime.utcnow(),
      confirmations_sent=0,
      wall_throws=0,
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
  me = anvil.server.session.get('me', False)
  if not me:
    return {
      'success': False,
      'msg': 'not logged in',
    }
  
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
      account_created=datetime.utcnow(),
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
  me = anvil.server.session.get('me', False)
  if not me:
    return {
      'success': False,
      'msg': 'not logged in',
    }
  
  
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
    start_session()
    
    
    # pre-activate games that dummy was in already
    existing_games = app_tables.games.search(player_1=me)
    
    for game in existing_games:
      game['p1_enabled'] = True
      game['throws'] = -1
  
    return {'success': True, 
            'msg': 'confirmed',
            'goto_login': False,
            'user': me,}
  
  else:
    return {'success': False,
            'goto_login': False,
            'msg': 'code incorrect',}
