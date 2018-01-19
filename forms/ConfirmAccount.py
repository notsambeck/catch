from anvil import *
import anvil.server
import anvil.users

from utils import is_valid_number
from Title import Title

class ConfirmAccount (ConfirmAccountTemplate):
  def __init__(self, phone, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)
    self.phone = phone

    # Any code you write here will run when the form opens.
    self.title_panel.add_component(Title())
    
    # alert('Your Catch confirmation code is:\n{}'.format(twilio_code), title='SMS INCOMING...')
    self.resend_button.text = 'Resend confirmation text to {}.'.format(self.phone)

  def go(self, **event_args):
    '''
    CONFIRM NEW ACCOUNT
    '''
    if not len(self.confirmation_code.text):
      Notification('You did not enter a confirmation code', title='Enter code').show()
      return False

    confirmed = anvil.server.call('confirm_account', self.confirmation_code.text, self.phone)
    if confirmed['success']:
      Notification('Account confirmed.', title='Success!')
      open_form('AddContacts')
    else:
      alert(confirmed['msg'])
      if confirmed['goto_login']:
        open_form('Login')

  def resend_button_click (self, **event_args):
    # This method is called when the button is clicked
    anvil.server.call('send_authorization_message', self.phone)
