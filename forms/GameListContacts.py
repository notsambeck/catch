from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables
from AddContacts import AddContacts

import colors_day as colors
    
class GameListContacts (GameListContactsTemplate):
  '''
  GameListElement renders an entire row (game) as a status grid entry
  
  1 game per gameListElement instance
  '''
  def __init__(self, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)
    
    # set self.me, self.you, self.am0
    self.me = anvil.users.get_user()
        
    self.set_event_handler('x-collapse', self.collapse)
    
  def expand(self, **event_args):
    # This method is called when the link is clicked
    # self.parent.raise_event_on_children('x-collapse')
    # get_open_form().collapse_except_id('bottom_contacts')
    self.game_view.add_component(AddContacts())
    self.game_summary.visible = False

  def collapse(self, **kwargs):
    self.game_view.clear()
    self.game_summary.visible = True
