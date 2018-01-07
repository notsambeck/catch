from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables

class ItemTemplate1(ItemTemplate1Template):

  def __init__(self, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)

    # Any code you write here will run when the form opens.

  def button_1_click (self, **event_args):
    # This method is called when the button is clicked
    open_form('play_catch')
    
    # this needs to point to correct game ID

