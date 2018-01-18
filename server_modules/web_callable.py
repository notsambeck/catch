import anvil.secrets
import anvil.users
import tables
from tables import app_tables
import anvil.server
import bcrypt

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

@anvil.server.callable
def do_login(phone, password):
  '''set anvil.session['user'] to the user with phone number'''
  me = get_user_by_phone(phone)
  if me:
    if password == me['password']:
      anvil.users.force_login(me)
      print("success")
      return anvil.users.get_user()
    else:
      print("invalid password")
      return False
  else:
    print("this account does not exist")
    return False

 
@anvil.server.callable
def create_user(phone, password, username):
  '''
  Create a new user.
  
  args: phone, password, username

  returns: True if success; False if user already exists
  '''
  if get_user_by_phone(phone):
    # 
    return False
  else:
    # TODO: enabled should be false until user confirms phone number (twilio) but this is not set up yet
    me = app_tables.users.add_row(enabled=True,
                                  # signed_up='12/25/2017',
                                  password=password,
                                  phone_number=int(phone),
                                  username=username,)
    if do_login(phone, password):
      return meusers
    else:
      print('error logging in but user may have been created')


def get_user_by_phone(phone):
  '''return users row for a phone number, or false if it does not exist
  TODO: this is a hilarious security flaw; literally returns the password for any phone number (ha!)'''
  return app_tables.users.get(phone_number=int(phone))


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