from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables
from utils import is_valid_number, hash_phone
from Title import Title
from GameList import GameList


class AddContacts (AddContactsTemplate):
  def __init__(self, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.title_panel.add_component(Title())
    self.game_list_panel.add_component(GameList())

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
      Notification(new_conn['msg']).show()
    else:
      c = confirm('{} does not have an account. Invite them to play Catch?'.format(phone))
      if c:
        alert('''
            Copy and paste this message!
            
            Let's play Catch. Hey... it's free.
            https://playcatch.anvilapp.net
            ''',
            title='')
        anvil.server.call('create_dummy', phone)
        new_conn = anvil.server.call('add_connection', phone)

  def why_phone_click(self, **event_args):
    # This method is called when the why_phone button is clicked
    alert('''
          This phone number is your friend's user ID.
          If your friend already has an account, this will connect you.
          We will never share this phone number with anyone, period.
          ''',
          title='Why we need a phone number:')

  def button_1_click(self, **event_args):
    # This method is called when the button is clicked
    open_form('GameList')

  def phone_pressed_enter(self, **event_args):
    # This method is called when the user presses Enter in this text box
    self.add_connection()

 