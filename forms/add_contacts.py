from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables
from validators import is_valid_number

class add_contacts (add_contactsTemplate):
  def __init__(self, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.my_connections = anvil.server.call('get_connections')
    self.repeating_panel_1.items = self.my_connections

  def explain_phone(self, **event_args):
    # This method is called when the why_phone button is clicked
    alert('''Your phone number is your user ID, so your friends can find you and play catch. 
          You will receive one SMS message to confirm this is your number, that's it!
          We will never share your number with anyone.''', title='Why we need your phone number:')

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
    other_id = anvil.server.call('check_user_exists', number)

    if other_id:
      # check if connection between users already exists
      for conn in self.my_connections.search():
        if conn['recipient'] == other_id:
          # TODO: this is probably an unneccessary warning
          alert('you are already connected to this user')
          return True
      else:  # finally
        alert('adding connection')
        anvil.server.call('add_connection', other_id)
    else:
      alert('that user does not seem to exist')


  def why_phone_click (self, **event_args):
    # This method is called when the why_phone button is clicked
    alert('''This phone number is your friend's user ID.
          If your friend already has an account, this will connect you.
          If not, you will have the option to send a message to invite them to play Catch.
          We will never share this phone number with anyone.''', title='Why we need a phone number:')

  def button_1_click (self, **event_args):
    # This method is called when the button is clicked
    open_form('game_list')




    
    
        


