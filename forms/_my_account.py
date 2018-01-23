from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables
from PlayCatch import PlayCatch
from GameList import GameList
from AddContacts import AddContacts

class _my_account (_my_accountTemplate):
  def __init__(self, game=None, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)

    # Any code you write here will run when the form opens.

    # self.content_panel.width = default by default
    # self.w = int(str([char for char in self.content_panel.width if char in '1234567890']))
    
    me = anvil.users.get_user()
    self.handle_label.text = me['handle']
    self.phone_number_label.text = me['phone_hash']
    my_games = anvil.server.call_s('get_games')
    if not my_games['success']:
      return False
    throws = 0
    for game in my_games['order']:
      throws += my_games['games'][game]['throws']
    throws += me['wall_throws']
   
    self.throws_label.visible = True
    self.throws_label.text = str(throws)
    
    self.color1.background = self.text_box_3.placeholder
    self.color2.background = self.text_box_4.placeholder
    self.reset_go_button.enabled = False
    
    # print(name)
    self.handle_label_top.text = 'logged in as: {}'.format(me['handle'])

  def logout_button_click (self, **event_args):
    # This method is called when the button is clicked
    anvil.users.logout()
    open_form('_login')

  def button_2_click (self, **event_args):
    # This method is called when the button is clicked
    self.text_box_1.visible = True
    self.text_box_2.visible = True
    self.reset_go_button.visible = True
    self.reset_go_button.enabled = False

  def button_1_click (self, **event_args):
    # This method is called when the button is clicked
    open_form('_play')


