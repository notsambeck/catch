from anvil import *
import anvil.server
import anvil.users

from utils import is_valid_number


class ConfirmAccount (ConfirmAccountTemplate):
  def __init__(self, phone, remember_me, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)
    self.phone = phone
    self.remember_me = remember_me
 
    # alert('Your Catch confirmation code is:\n{}'.format(twilio_code), title='SMS INCOMING...')
    self.resend_button.text = 'Resend confirmation text to {}.'.format(self.phone)

  def go(self, **event_args):
    '''
    CONFIRM NEW ACCOUNT
    '''
    if not len(self.confirmation_code.text):
      Notification('You did not enter a confirmation code', title='Enter code').show()
      return False

    resp = anvil.server.call('confirm_account', self.confirmation_code.text, self.phone, self.remember_me)
    if resp['success']:
      Notification('Account confirmed.', title='Success!')
      open_form('PlayScreen', resp['user'])
    else:
      alert(resp['msg'])
      if resp['goto_login']:
        open_form(Login())

  def resend_button_click (self, **event_args):
    # This method is called when the button is clicked
    anvil.server.call('send_authorization_message', self.phone)
