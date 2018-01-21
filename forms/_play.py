from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables
from PlayCatch import PlayCatch

class _play (_playTemplate):
  def __init__(self, game, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)

    # Any code you write here will run when the form opens.

    self.xy_panel_1.width = self.content_panel.width 
    self.xy_panel_1.height = self.content_panel.width
    
    _frame = PlayCatch(game)
    _frame.height = '250px'
    self.xy_panel_1.add_component(_frame, x=50, y=50, width=700)

    print(self.xy_panel_1.height)
    self.logged_in_label.txt = 'logged in as: {}'.format(anvil.users.get_user()['handle'])
    
  def logout_button_click (self, **event_args):
    # This method is called when the button is clicked
    anvil.users.logout()
    open_form('_login')
