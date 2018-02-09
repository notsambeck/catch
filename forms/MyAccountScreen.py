from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables
from utils import is_valid_color
import colors_day as colors

from utils import ErrorHandler
error_handler = ErrorHandler(alert, open_form)


class MyAccountScreen (MyAccountScreenTemplate):
  def __init__(self, view='account', **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)

    # Any code you write here will run when the form opens.

    # self.content_panel.width = default by default
    # self.w = int(str([char for char in self.content_panel.width if char in '1234567890']))
    set_default_error_handling(error_handler)
    
    self.me = anvil.users.get_user()
    self.view = view
    
    self.handle_label.text = self.me['handle']
    self.phone_number_label.text = self.me['phone_hash']

    # print(name)
    self.handle_label_top.text = 'logged in as: {}'.format(self.me['handle'])

  def logout_button_click (self, **event_args):
    # This method is called when the button is clicked
    anvil.server.call('delete_cookie')
    anvil.users.logout()
    open_form('LoginScreen')

  def password_button_click (self, **event_args):
    # This method is called when the button is clicked
    self.text_box_1.visible = True
    self.text_box_2.visible = True
    self.reset_go_button.visible = True
    self.reset_go_button.enabled = False

  def color_set_button_click (self, **event_args):
    # This method is called when the button is clicked
    c1 = is_valid_color(self.enter_color_1.text)
    c2 = is_valid_color(self.enter_color_2.text)
    
    if not c1 or not c2:
      Notification('Please enter TWO valid colors. 6 hex digits RRGGBB: 0-9/A-F').show()
      return False

    self.color1.background = '#' + c1
    self.color2.background = '#' + c2
    
    update = anvil.server.call('update_colors', self.enter_color_1.text, self.enter_color_2.text)
    if update['success']:
      self.me = update['user']

  def back_to_games_button_click(self, **event_args):
    # This method is called when the button is clicked
    self.content_panel.clear()
    open_form('PlayScreen', self.me)

  def content_panel_show (self, **event_args):
    # This method is called when the column panel is shown on the screen
    if self.view == 'account':
      my_games = anvil.server.call_s('get_games')
      
      if not my_games['success']:
        Notification(my_games['msg']).show()
      
      throws = 0
      for game in my_games['order']:
        throws += my_games['games'][game]['throws']
      throws += self.me['wall_throws']
    
      self.throws_label.visible = True
      self.throws_label.text = str(throws)
      
      if self.me['color_1']:
        self.enter_color_1.text = self.me['color_1']
      else:
        self.enter_color_1.text = colors.black
      if self.me['color_2']:
        self.enter_color_2.text = self.me['color_2']
      else:
        self.enter_color_2.text = colors.skin 
      
      self.color1.background = self.enter_color_1.text
      self.color2.background = self.enter_color_2.text
      
      self.account_panel.visible = True
      return
      
    if self.view == 'help':
      self.help_panel.visible = True

  def my_account_button_click (self, **event_args):
    # This method is called when the button is clicked
    self.account_panel.visible = True
    self.help_panel.visible = False

  def add_home_button_click (self, **event_args):
    # This method is called when the button is clicked
    self.account_panel.visible = False
    self.help_panel.visible = True


