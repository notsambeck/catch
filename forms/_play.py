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

    self.content_panel.width = ???????
    print(self.w)
    # self.w = int(str([char for char in self.content_panel.width if char in '1234567890']))
    self.xy_panel_1.width = self.w
    self.xy_panel_1.height = self.w * 3 // 4
    
    _frame = PlayCatch(game)
    _frame.height = self.w // 3
    self.xy_panel_1.add_component(_frame, x=self.w//10, y=self.w//10, width=self.w/2)

    print(self.xy_panel_1.height)
    self.logged_in_label.txt = 'logged in as: {}'.format(anvil.users.get_user()['handle'])
    
  def logout_button_click (self, **event_args):
    # This method is called when the button is clicked
    anvil.users.logout()
    open_form('_login')
