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

  def explain_phone(self, **event_args):
    # This method is called when the why_phone button is clicked
    alert('''Your phone number is your user ID, so your friends can find you and play catch. 
          You will receive one SMS message to confirm this is your number, that's it!
          We will never share your number with anyone.''', title='Why we need your phone number:')

  def go(self, **event_args):
    # This method is called when the submit button is clicked
    number = is_valid_number(self.phone.text)
    if not number:
      alert('Please enter 10-digit numeric phone number with area code.')
      return False

    if anvil.users.get_user()['phone_number'] == number:
      alert('That is your phone number; this does not make sense.')
      return False
    
    # valid phone number: check if user exists
    exists = anvil.server.call('check_user_exists', number)

    if exists:
      # check if connection between users already exists
      for conn in self.my_connections.search():
        if conn['recipient'] == exists:
          # TODO: this is probably an unneccessary warning
          alert('you are already connected to this user')
          return True
        else:
          anvil.server.call('add_connection', exists)


  def why_phone_click (self, **event_args):
    # This method is called when the why_phone button is clicked
    alert('''This phone number is your friend's user ID.
          If your friend already has an account, this will connect you.
          If not, you will have the option to send a message to invite them to play Catch.
          We will never share this phone number with anyone.''', title='Why we need a phone number:')


    
    
        


