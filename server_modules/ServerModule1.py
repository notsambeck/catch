import anvil.users
import tables
from tables import app_tables
import anvil.server

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
@anvil.server.callable
def start_game(recipient):
      app_tables.games.add_row(initiator=anvil.users.get_user(),
                               recipient=recipient,
                               initiator_has_ball=False)

@anvil.server.callable
def do_login(phone, password):
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
  me = app_tables.users.get(phone_number=int(phone))
  if me:
    print("user already exists")
    return False
  else:
    # enabled should be false until user confirms phone number (twilio)
    app_tables.users.add_row(enabled=True,
                             # signed_up='12/25/2017',
                             # last_login='12/25/17',
                             password=password,
                             phone_number=int(phone),
                             name=username,)
    do_login(phone, password)
    return True