from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables
from utils import is_valid_number, hash_phone
from Title import Title
from GameList import GameList
from Status import Status


class AddContacts (AddContactsTemplate):
  def __init__(self, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)

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
    new_conn = anvil.server.call('add_connection', phone)

    if new_conn['success']:
      if new_conn['enabled']:
        Notification(new_conn['msg']).show()
      else:
        # new connection exists but not enabled. remind them to play
        c = confirm("{} was already invited to play Catch, but hasn't tried it. Remind them?".format(phone))
        if c:
          alert('''Let's play Catch, it's mad popular!
                https://playcatch.anvilapp.net''',
                title='Copy and paste this message')
    else:
      c = confirm('{} does not have an account. Invite them to play Catch?'.format(phone))
      if c:
        alert('''Let's play Catch. Hey... it's free.
            https://playcatch.anvilapp.net''',
            title='Copy and paste this message')
        dummy = anvil.server.call('create_dummy', phone)
        
        if not dummy['success']:
          alert(dummy['msg'])
          return False
        
        new_conn = anvil.server.call('add_connection', phone)
        if not new_conn['success']:
          alert(new_conn['msg'])
          return False
        
        self.game_list_panel.get_components()[0].add_connection(new_conn['game'])

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

 