from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables
from Login import Login


def error_handler(err):
  # TODO: change this behaviour for release
  me = anvil.server.call('start_session')
  if me:
    open_form('PlayScreen', me)
  else:
    open_form('LoginScreen')


class LoginScreen (LoginScreenTemplate):
  def __init__(self, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)
    
    set_default_error_handling(error_handler)
    self.content_panel.add_component(Login())
    
    # anvil.server.call('delete_cookie')
    anvil.server.reset_session()
    
