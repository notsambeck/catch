import anvil.users
import tables
from tables import app_tables
import anvil.server

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.

@anvil.server.callable
def do_login(phone, password):
  '''set anvil.session['user'] to the user with phone number'''
  me = app_tables.users.get(phone_number=int(phone))
  if me:
    if password == me['password']:
      anvil.users.force_login(me)
      print("success")
      print(anvil.users.get_user())
      return True
    else:
      print("invalid password")
      return False
  else:
    print("this account does not exist")
    return False

 
@anvil.server.callable
def make_new_user(phone, password, username):
  '''
  Create a new user.
  
  args: phone, password, username
    
  returns: True if success; False if user already exists
  '''
  if check_user_exists(phone):
    return False
  else:
    # TODO: enabled should be false until user confirms phone number (twilio) but this is not set up yet
    app_tables.users.add_row(enabled=True,
                             # signed_up='12/25/2017',
                             password=password,
                             phone_number=int(phone),
                             username=username,)
    do_login(phone, password)
    return True


@anvil.server.callable
def check_user_exists(phone):
  '''return user ID for a phone number, or false if it does not exist'''
  u = app_tables.users.get(phone_number=int(phone))
  if u:
    return u.get_id()
  else:
    return False


@anvil.server.callable
def add_connection(other_id):
  '''adds a connection initiated by current user to other_user and vice versa.
  args:
    other_user: row from table
  '''
  print('adding connection')
  other_user = app_tables.users.get_by_id(other_id)
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
    return app_tables.connections.client_readable(initiator=me)


@anvil.server.callable
def get_game_status(connection_id):
  '''get the status of a connection from perspective of logged in user; 
  start game if not happening
  return True if I have ball, else False'''
  game = app_tables.connections.get_by_id(connection_id)
  if not game['game_ongoing']:
    game.update(game_ongoing=True, initiator_has_ball=True)
    game['dual'].update(game_ongoing=True, initiator_has_ball=False)
  
  return game


@anvil.server.callable
def throw(game_id):
  game = app_tables.connections.get_by_id(game_id)
  game['initiator_has_ball'] = False
  game['dual']['initiator_has_ball'] = True
  

@anvil.server.callable
def some_connection():
  do_login('5555555555', '5')
  return get_connections().search()[0].get_id()