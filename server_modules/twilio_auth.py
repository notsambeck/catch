import anvil.secrets
import anvil.users
import tables
from tables import app_tables
import anvil.server

from twilio.rest import Client

# Find these values at https://twilio.com/user/account

# test id
account_sid = 'AC8c06108afa619c6f98486555b0d09d8c'
auth_token = anvil.secrets.get_secret('twilio_test_auth')

client = Client(account_sid, auth_token)

# TODO: this needs to not be callable

@anvil.server.callable
def send_authorization_message(code):
  message = client.messages.create(
    to="+15035053813",
    from_="+15005550006",
    body=code,
  )
  print(message.sid)