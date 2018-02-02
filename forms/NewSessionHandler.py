from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables

from utils import ErrorHandler
error_handler = ErrorHandler(alert, open_form)


class NewSessionHandler (NewSessionHandlerTemplate):
  def __init__(self, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)
    anvil.server.reset_session()
    set_default_error_handling(error_handler)

  def form_show (self, **event_args):
    # This method is called when the column panel is shown on the screen
    sess = anvil.server.call('start_session')
    if sess['success']:
      print(sess['msg'])
      open_form('PlayScreen', user=sess['user'])
    else:
      print(sess['msg'])
      open_form('LoginScreen')
