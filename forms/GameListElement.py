from anvil import *
import anvil.server
import anvil.users
import tables
from tables import app_tables
from PlayCatch import PlayCatch

from datetime import datetime
import colors_day as colors
    
class GameListElement(GameListElementTemplate):
  '''
  GameListElement renders an entire row (game) as a status grid entry
  
  1 game per gameListElement instance
  '''
  def __init__(self, user, game, **properties):
    # You must call self.init_components() before doing anything else in this function
    self.init_components(**properties)
    
    # self.game is ENTIRE ROW!
    self.game = game
    self.child = None
    
    # set self.me, self.you, self.am0
    self.me = user
    self.am0 = self.game['player_0'] == self.me
    self._id = game.get_id()
    
    if self.am0:
      if self.game['p1_enabled']:
        self.you = self.game['player_1']['handle']
      else:
        self.you = self.game['player_1']['phone_hash']
    else:
      if self.game['p1_enabled']:
        self.you = self.game['player_0']['handle']
      else:
        self.you = self.game['player_0']['phone_hash']
             
    # me: colors
    # print(self.me['color_1'])
    if self.me['color_1']:
      self.my_color_1 = self.me['color_1']
    else:
      self.my_color_1 = colors.black
    # print(self.me['color_2'])
    if self.me['color_2']:
      self.my_color_2 = self.me['color_2']
    else:
      self.my_color_2 = colors.skin
      
    # opp: colors if am0
    if self.am0:
      if self.game['player_1']['color_1']:
        self.opp_color_1 = self.game['player_1']['color_1']
      else:
        self.opp_color_1 = colors.black
      if self.game['player_1']['color_2']:
        self.opp_color_2 = self.game['player_1']['color_2']
      else:
        self.opp_color_2 = colors.skin
      
    # opp: colors if not am0
    else:
      if self.game['player_0']['color_1']:
        self.opp_color_1 = self.game['player_0']['color_1']
      else:
        self.opp_color_1 = colors.black
      if self.game['player_0']['color_2']:
        self.opp_color_2 = self.game['player_0']['color_2']
      else:
        self.opp_color_2 = colors.skin

    self.set_labels()
    self.set_event_handler('x-collapse', self.collapse)
    
  def set_labels(self):
    # clear
    self.background = colors.white
 
    # is_active is status for any ongoing game (not highlighted only)
    if self.game['is_active']:
      time = self.game['last_throw_time']
      time = time.replace(tzinfo=None)
      now = datetime.utcnow()
      
      # TODO: fix 23 hours bug here
      delta = now - time
      # print(delta)
      if delta.days > 1:
        timestring = '{} days ago'.format(delta.days)
      elif delta.days == 1:
        timestring = '1 day ago'
      else:
        if delta.seconds > 3600:
          timestring = '{} hours ago'.format(delta.seconds // 3600)
        else:
          timestring = '{} minutes ago'.format(delta.seconds // 60)

      if (self.am0 and self.game['has_ball'] == 0) or (not self.am0 and self.game['has_ball'] == 1):
        self.status_label.text = '{} threw you ball {}'.format(self.you,
                                                                timestring,)
        self.status_label.foreground = colors.grass
      else:
        self.status_label.text = 'You threw ball to {} {}'.format(self.you,
                                                                  timestring,)
        self.status_label.foreground = colors.building1

    # game inactive but both ready
    elif self.game['p1_enabled']:  
      self.status_label.text = 'Start game with {}!'.format(self.you)
      self.status_label.foreground = colors.black
      self.background = colors.highlight

    # player 2 not yet enabled      
    else:
      self.status_label.text = 'Player {} not activated'.format(self.you)
      self.status_label.foreground = colors.gray
   
  def update(self, updated_game):
    self.game = updated_game
    if self.child:
      self.child.update(updated_game)
    else:
      self.set_labels()

  def expand(self, **event_args):
    start = datetime.utcnow()
    if not self.game['p1_enabled']:
      return False
    # This method is called when the link is clicked
    # with Notification('Loading game...'):
    # self.parent.raise_event_on_children('x-collapse')
    
    # print('TIMING...')
    top = get_open_form()
    top.collapse_except_id(self.game)
    #print('TIME: {}'.format(str(datetime.utcnow() - start)))
    
    self.child = PlayCatch(self.game, self.me, self)
    self.game_view.add_component(self.child)
    self.game_summary.visible = False
    self.background = colors.white
    
  def collapse(self, x, **kwargs):
    if x == self.game:
      # print('Collapse: not collapsing self')
      return
    self.game_view.clear()
    self.child = None
    self.game_summary.visible = True
