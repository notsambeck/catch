from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables
from PlayCatch import PlayCatch
from GameList import GameList
from AddContacts import AddContacts
from GameListElement import GameListElement

class _play_copy (_play_copyTemplate):
  def __init__(self, game=None, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)

    # Any code you write here will run when the form opens.

    # self.content_panel.width = default by default
    # self.w = int(str([char for char in self.content_panel.width if char in '1234567890']))
    
    self.linear_panel_1.add_component(AddContacts())
    
    my_games = anvil.server.call_s('get_games')
    if my_games['success']:
      self.linear_panel_2.add_component(GameListElement(my_games['games'][my_games['order'][0]]))
    
    name = anvil.users.get_user()['handle']
    # print(name)
    self.handle.text = 'logged in as: {}'.format(name)
    
  def logout_button_click (self, **event_args):
    # This method is called when the button is clicked
    anvil.users.logout()
    open_form('_login')

  def button_1_click (self, **event_args):
    # This method is called when the ADD CONTACTS button is clicked
    self.linear_panel_1.clear()
    self.linear_panel_1.add_component(AddContacts())
    self.linear_panel_2.get_components()[0].clear_highlights()

  def cccount_click (self, **event_args):
    # This method is called when the button is clicked
    open_form('_my_account')