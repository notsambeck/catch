from anvil import *
import anvil.server


class NewSessionHandler (NewSessionHandlerTemplate):
  def __init__(self, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)
    anvil.server.reset_session()

  def form_show (self, **event_args):
    # This method is called when the column panel is shown on the screen
    sess = anvil.server.call('start_session')
    if sess['success']:
      print(sess['msg'])
      open_form('PlayScreen', user=sess['user'])
    else:
      print(sess['msg'])
      open_form('LoginScreen')
