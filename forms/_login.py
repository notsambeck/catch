from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables
from Login import Login

class _login (_loginTemplate):
  def __init__(self, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)
    
    # anvil.server.call('delete_cookie')

    if anvil.users.get_user(allow_remembered=True):
      print('already logged in')
      open_form('_play')
    
      x
    else:
      self.content_panel.add_component(Login())