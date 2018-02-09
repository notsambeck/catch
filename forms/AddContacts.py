from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables
from utils import is_valid_number, hash_phone
import colors_day as colors


class AddContacts (AddContactsTemplate):
  def __init__(self, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)
    self.go_button.background = colors.highlight

  def add_connection(self, **event_args):
    # This method is called when the submit button is clicked
    phone = is_valid_number(self.phone.text)

    if not phone:
      alert('Please enter 10-digit numeric phone number with area code.')
      return False

    if anvil.users.get_user()['phone_hash'] == hash_phone(phone):
      alert('That is your phone number; this does not make sense.')
      return False
    
    # valid phone number: check if user exists
    user_check = anvil.server.call_s('get_user_id_status_by_phone', phone)
    if not user_check['success']:
      Notification(user_check['msg']).show()
      return False

    elif user_check['exists'] and user_check['enabled']:
      connection = anvil.server.call('add_connection', phone)
      if connection['success']:
        get_open_form().add_game(connection['game'])
      Notification(connection['msg']).show()
    
    elif user_check['exists'] and not user_check['enabled']:
      # new connection exists but not enabled. remind them to play?
      connection = anvil.server.call('add_connection', phone)
      Notification(connection['msg']).show()
      get_open_form().add_game(connection['game'])
      
      c = confirm("{} was already invited to play Catch, but hasn't activated their account. Remind them?".format(phone))
      if c:
        alert('''Let's play Catch, it's wicked popular!
              https://playcatch.anvilapp.net''',
              title='Copy this message and text it!')

      
    elif not user_check['exists']:
      c = confirm('{} does not have an account. Do you want to invite them?'.format(phone))
      if c:
        alert('''Let's play Catch. Hey... it's free.
            https://playcatch.anvilapp.net''',
            title='Copy this message and send it!')
        dummy_connection = anvil.server.call('create_dummy', phone)
        Notification(dummy_connection['msg']).show()
        get_open_form().add_game(dummy_connection['game'])
      
    else:
      Notification(user_check['msg']).show()


  def why_phone_click(self, **event_args):
    # This method is called when the why_phone button is clicked
    alert('''
          This phone number is your friend's user ID.
          If your friend already has an account, this will connect you.
          We will never share this phone number with anyone, period.
          ''',
          title='Why we need a phone number:')

  def phone_pressed_enter(self, **event_args):
    # This method is called when the user presses Enter in this text box
    self.add_connection()

 