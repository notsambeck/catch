import anvil.secrets
import anvil.users
import tables
from tables import app_tables
import anvil.server

from utils import hash_phone

from twilio.rest import Client

# Find these values at https://twilio.com/user/account

# test id
account_sid = anvil.secrets.get_secret('twilio_sid')
auth_token = anvil.secrets.get_secret('twilio_token')

client = Client(account_sid, auth_token)

@anvil.server.callable
def send_authorization_message(phone):
  '''
  sends SMS with code to phone number up to 3 times.
  '''
  user = app_tables.users.get(phone_hash=hash_phone(phone))
  if not user:
    return {'success': False,
            'msg': 'no account for {}; please create a new account.'.format(phone)}
  
  elif user['enabled']:
    return {'success': False,
            'msg': 'account already verified, just log in'}
  
  elif user['confirmations_sent'] > 3:
    return {'success': False,
            'msg': 'We have sent > 3 confirmation messages. Please contact customer service.'}
  
  elif user['dummy']:
    return {'success': False,
            'msg': "Check 'create new account' to create your password"}

  else:
    
    if phone == "5037569645":
      sendto = "+15037569645"
    else:
      sendto = "+15035053813"
     
    try:
      message = client.api.account.messages.create(
        # to="+1{}".format(phone),     # TODO
        to=sendto,
        from_="+15035582695",
        body="{}: Your CATCH authentication code is: {}".format(phone, user['twilio_code'])
      )
      user['confirmations_sent'] += 1
      return {'success': True,
            'msg': 'message sent'}
    
    except TwilioError:
      return {'success': False,
              'msg': 'conf message attempted, but failed to send'}
      
