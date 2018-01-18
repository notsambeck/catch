from anvil import *
import anvil.server
import anvil.users

from validators import is_valid_number
from Title import Title

class ConfirmAccount (ConfirmAccountTemplate):
  def __init__(self, twilio_code, user_id, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)
    self.code = twilio_code  # TODO: fake
    self.user_id = user_id
    anvil.server.reset_session()

    # Any code you write here will run when the form opens.
    self.title_panel.add_component(Title())
    
    alert('Your Catch confirmation code is:\n{}'.format(twilio_code),
          title='SMS INCOMING...')

  def go(self, **event_args):
    '''
    CONFIRM NEW ACCOUNT
    '''
    if not isinstance(self.confirmation_code.text, str):
      Notification('You did not enter a confirmation code', title='Enter code')
    
    confirmed = anvil.server.call('confirm_account', self.confirmation_code.text, self.user_id)
    if confirmed:
      Notification('Code is correct.', title='Success!')
      open_form('AddContacts')
    else:
      alert('INCORRECT CODE!')