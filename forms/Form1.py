from anvil import *
import anvil.users
import anvil.server
import tables
from tables import app_tables


class Form1(Form1Template):

  def __init__(self, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    anvil.users.login_with_form()

  def button_1_click (self, **event_args):
    # This method is called when the button is clicked
    self.game_status.text = "Playing catch: ", self.recipient.text, "&", anvil.users.get_user()
    anvil.server.call('start_game', int(self.recipient.text))