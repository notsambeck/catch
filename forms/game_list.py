from anvil import *
import anvil.users
import anvil.server
import tables
from tables import app_tables


class game_list (game_listTemplate):
  def __init__(self, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.repeating_panel_1.items = properties['conns']

  def button_1_click (self, **event_args):
    # This method is called when the button is clicked
    self.game_status.text = "Playing catch: " + self.recipient.text + " & " + anvil.users.get_user()['name']
    anvil.server.call('start_game', int(self.recipient.text))

  def add_contacts_click (self, **event_args):
    # This method is called when the button is clicked
    open_form('add_contacts')

  def recipient_pressed_enter (self, **event_args):
    # This method is called when the user presses Enter in this text box
    pass








