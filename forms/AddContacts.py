from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables
from validators import is_valid_number
from Title import Title
from GameGrid import GameGrid


class AddContacts (AddContactsTemplate):
  def __init__(self, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.title_panel.add_component(Title())
    self.conns = self.update_connections()

  def add_connection(self, **event_args):
    # This method is called when the submit button is clicked
    number = is_valid_number(self.phone.text)

    if not number:
      alert('Please enter 10-digit numeric phone number with area code.')
      return False

    if anvil.users.get_user()['phone_number'] == number:
      alert('That is your phone number; this does not make sense.')
      return False
    
    # valid phone number: check if user exists
    # either returns False, or row from user table
    other = anvil.server.call('get_user_by_phone', number)

    if other:
      # check if connection between users already exists
      for conn in self.conns:
        if conn['recipient'] == other:
          # TODO: this is probably an unneccessary warning
          Notification('you are already connected to this user').show()
          return True
      else:  # finally
        with Notification(''.join(['Adding connection to:', other['username']])):
          new_conn = anvil.server.call('add_connection', other.get_id())
          self.game_panel.add_component(GameGrid(new_conn))
    else:
      alert('''that user does not exist, please invite them to join at: 
            fzcmbv5jk6jlbkev.anvilapp.net/6FZXPZAN57OVOFH6M5E73C6V''')


  def why_phone_click(self, **event_args):
    # This method is called when the why_phone button is clicked
    alert('''
          This phone number is your friend's user ID.
          If your friend already has an account, this will connect you.
          If not, you will have the option to send a message to invite them to play Catch.
          We will never share this phone number with anyone.''',
          title='Why we need a phone number:')

  def update_connections(self):
    self.game_panel.clear()
    conns = anvil.server.call('get_connections')
    for conn in conns:
      self.game_panel.add_component(GameGrid(conn))
    return conns

  def button_1_click(self, **event_args):
    # This method is called when the button is clicked
    open_form('GameList')

  def timer_1_tick(self, **event_args):
    # This method is called Every [interval] seconds
    self.update_connections()

  def phone_pressed_enter(self, **event_args):
    # This method is called when the user presses Enter in this text box
    self.add_connection()

 