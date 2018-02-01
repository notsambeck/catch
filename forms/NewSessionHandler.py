from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables


def error_handler(err):
  # TODO: change this behaviour for release
  me = anvil.server.call('start_session')
  if me:
    open_form('PlayScreen', me)
  else:
    open_form('LoginScreen')


class NewSessionHandler (NewSessionHandlerTemplate):
  def __init__(self, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)
    set_default_error_handling(error_handler)

  def form_show (self, **event_args):
    # This method is called when the column panel is shown on the screen
    anvil.server.reset_session()
    sess = anvil.server.call('start_session')
    if sess['success']:
      print('already logged in')
      open_form('PlayScreen', user=sess['user'])
    else:
      cooky = anvil.server.call('has_stored_login')
      if cooky:
        open_form('PlayScreen', user=cooky)
      else:
        print('not logged in')
        open_form('LoginScreen')


