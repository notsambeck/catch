from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables
from AddContacts import AddContacts

class _games (_gamesTemplate):
  def __init__(self, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.content_panel.add_component(AddContacts())
    self.logged_in_label.txt = 'logged in as: {}'.format(anvil.users.get_user()['handle'])

  def logout_button_click (self, **event_args):
    # This method is called when the button is clicked
    anvil.users.logout()
    open_form('_login')

