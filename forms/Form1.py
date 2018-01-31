from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables
import datetime

class Form1(Form1Template):

  def __init__(self, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)
    self.label_1 = datetime.datetime.now()
    # Any code you write here will run when the form opens.