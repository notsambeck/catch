from anvil import *
import anvil.server
import anvil.users

from utils import is_valid_number
from ConfirmAccount import ConfirmAccount

class Login(LoginTemplate):
  def __init__(self, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)
    anvil.server.reset_session()


  def new_account_change(self, **args):
    # show or hide confirm password and user_name
    new_account = self.new_account.checked   # true or false
    self.label_confirm_password.visible = new_account
    self.label_name.visible = new_account
    self.confirm_password.visible = new_account
    self.user_name.visible = new_account
    self.explain_phone_button.visible = new_account
    self.confirmation_text_warn.visible = new_account
    if new_account:
      self.go_button.text = "Make new account"
    else:
      self.go_button.text = "Log in"

  def explain_phone(self, **event_args):
    # This method is called when the why_phone button is clicked
    alert('''Your phone number is your user ID, so your friends can find you and play catch. 
          You will receive one SMS message to confirm this is your number, that's it!
          We will never share your number with anyone.''', title='Why we need your phone number:')

  def go(self, **event_args):
    '''
    LOGIN
    or
    CREATE_USER
    
    This method is called when the submit button is clicked.
    Returns True on successful exit, else False'''

    number = is_valid_number(self.phone.text)
  
    if not number:
      alert('Please enter 10-digit numeric phone number with area code.')
      return False

    # NEW ACCOUNT
    if self.new_account.checked:
      if len(self.password.text) < 5:
        alert('Password too short.')
        return False
      elif self.confirm_password.text != self.password.text:
        alert('Passwords do not match.')
        return False
      elif not self.user_name.text:
        alert('Please enter a username (your friends will be able to see it).')
        return False
      else:
        user_created = anvil.server.call('create_user',
                                         self.phone.text,
                                         self.password.text,
                                         self.user_name.text,)
        if user_created['success']:
          Notification('account created').show()
          get_open_form().content_panel.clear()
          get_open_form().content_panel.add_component(ConfirmAccount(number))
        else:
          alert(user_created['msg'])

    # LOGIN
    else:
      status = anvil.server.call('do_login',
                                  number,
                                  self.password.text,
                                  self.persist.checked,)
      
      # if we have full access, continue
      if status['success'] and status['enabled']:
        Notification("Login successful...").show()
        open_form('_play')

      # if account not confirmed, go to confirmation
      elif status['success'] and not status['enabled']:
        Notification("Unverified account...").show()
        get_open_form().content_panel.clear()
        get_open_form().content_panel.add_component(ConfirmAccount(number))

      # else: fail
      else:
        Notification(status['msg']).show()

