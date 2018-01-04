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