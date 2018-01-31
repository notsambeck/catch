from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables
from Login import Login

class LoginScreen (LoginScreenTemplate):
  def __init__(self, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)
    
    # anvil.server.call('delete_cookie')
    anvil.server.reset_session()
    
  def form_show(self, **event_args):
    # This method is called when the HTML panel is shown on the screen
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
        self.content_panel.add_component(Login())
