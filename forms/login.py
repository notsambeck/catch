from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables
from validators import is_valid_number

class login (loginTemplate):
  def __init__(self, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)

    # Any code you write here will run when the form opens.

  def new_account_change(self, **args):
    # show or hide confirm password and user_name
    new_account = self.new_account.checked   # true or false
    self.label_confirm_password.visible = new_account
    self.label_name.visible = new_account
    self.confirm_password.visible = new_account
    self.user_name.visible = new_account
    self.explain_phone_button.visible = new_account
    if new_account:
      self.go_button.text = 'Make new account'
    else:
      self.go_button.text = 'Log in'

  def explain_phone(self, **event_args):
    # This method is called when the why_phone button is clicked
    alert('''Your phone number is your user ID, so your friends can find you and play catch. 
          You will receive one SMS message to confirm this is your number, that's it!
          We will never share your number with anyone.''', title='Why we need your phone number:')

  def go(self, **event_args):
    '''This method is called when the submit button is clicked
    Returns True on successful exit, else False'''
    number = is_valid_number(self.phone.text)
  
    if not number:
      alert('Please enter 10-digit numeric phone number with area code.')
      return False

    if self.new_account.checked:
      if len(self.password.text) < 6:
        alert('Password must be at least 6 characters.')
        return False
      elif self.confirm_password.text != self.password.text:
        alert('Passwords do not match.')
        return False
      elif not self.user_name.text:
        alert('Please enter a user name.')
        return False
      else:
        user_created = anvil.server.call('make_new_user',
                                         self.phone.text,
                                         self.password.text,
                                         self.user_name.text,)
        if user_created:
          open_form('add_contacts')
    else:    # login
      success = anvil.server.call('do_login', self.phone.text, self.password.text)
      if success:
        open_form('game_list')
