import anvil.secrets
import anvil.users
import tables
from tables import app_tables
import anvil.server

from utils import is_valid_number, is_valid_color, hash_phone, generate_code
from twilio_auth import send_authorization_message

from datetime import datetime
debug = False


@anvil.server.callable
def get_games(wall_throws=0, robot_throws=0, server=False, quick=False):
  '''
  get all the connections for current user
  
  also updates wall_throws
  
  returns {'success': bool,
           'msg': status message,
           'order': list of game ids in order
           'games': {game_id: game},}
  '''
  if debug:
    print('get_games(quick={})'.format(str(quick)))
    
  start_time = datetime.utcnow()
    
  me = anvil.server.session.get('me', False)
  if not me:
    return {
      'success': False,
      'msg': 'not logged in',
    }
   
  app_tables.users.get_by_id(me.get_id())['wall_throws'] = max(wall_throws, app_tables.users.get_by_id(me.get_id())['wall_throws'])
  app_tables.users.get_by_id(me.get_id())['robot_throws'] = max(robot_throws, app_tables.users.get_by_id(me.get_id())['robot_throws'])

  games = {}
  order = []
  waiting = []

  with tables.Transaction() as txn:
    # update from stored game list instead of searching
    if anvil.server.session.get('order', False) and quick:
      games = {_id: app_tables.games.get_by_id(_id) for _id in anvil.server.session['order']}
      msg = 'quick retrieved {} games in {}'
      order = anvil.server.session['order']
      
    else:
      game_list = [game for game in app_tables.games.search(tables.order_by('throws', ascending=False))]
      msg = 'retrieved all {} games in {}'
      for game in game_list:
        if game['player_0'] == me or game['player_1'] == me:
          _id = game.get_id()
          if not game['p1_enabled']:
            waiting.append(_id)
          else:
            order.append(_id)
          games[_id] = game
      # endfor
      order += waiting
      anvil.server.session['order'] = order   # [_id]
    
  msg = msg.format(len(order), datetime.utcnow()-start_time)
  
  # internal use to generate game list for new user
  if server:
    return games

  return {'success': True,
          'msg': msg,
          'order': order,
          'robot_throws': app_tables.users.get_by_id(me.get_id())['robot_throws'],
          'wall_throws': app_tables.users.get_by_id(me.get_id())['wall_throws'],
          'games': games,}


@anvil.server.callable
def make_game_active(game_id):
  '''
  get the status of a game; 
  start game if not already active;
  give activating user (me) the ball
  
  return game row or False
  '''
  if debug:
    print('make_game_active')
    
  me = anvil.server.session.get('me', False)
  if not me:
    return {
      'success': False,
      'msg': 'not logged in',
    }
      
  game = app_tables.games.get_by_id(game_id)
  
  if game['player_0'] == me:
    has_ball = 0
  elif game['player_1'] == me:
    has_ball = 1
  else: 
    return {'success': False,
            'msg': 'you are not in this game',}

  if game['is_active']:
    return {'success': False,
            'msg': 'make_game_active: game is already active'}
      
  with tables.Transaction() as txn:
    # USER ACTIONS LOG
    app_tables.user_actions.add_row(user=me, action_type='activate_game', time=datetime.utcnow())
    
    game['is_active'] = True
    game['has_ball'] = has_ball
    game['game_start_time'] = datetime.utcnow()
    game['throws'] = 0
  # print('set game', game['player_1']['handle'], 'vs', game['player_2']['handle'], '.is_active to:', game['is_active'])
  return {'success': True,
          'game': game}


@anvil.server.callable
def throw(game_id):
  '''
  User pressed throw; 
  move ball pointer in database;
  return game row.
  '''
  if debug:
    print('throw()')
  # print('throw() called at {}'.format(game_id))
  
  me = anvil.server.session.get('me', False)
  if not me:
    return {
      'success': False,
      'msg': 'not logged in',
    }
  
  game = app_tables.games.get_by_id(game_id)
  if not game['is_active']:
    return {'success': False, 
            'msg': 'Must activate game before throwing.'}
  
  has_ball = 'player_{}'.format(game['has_ball'])
  # print(has_ball, ' has the ball now. name: ', game[has_ball]['handle'])

  if game[has_ball] != me:
    return {'success': False,
            'msg': 'you did not have the ball'}

  # send notification to add game to home screen
  add_home = me['is_new']

  # print('setting:')
  with tables.Transaction() as txn:

    game['has_ball'] = abs(1 - game['has_ball'])  # flip who has ball
    game['throws'] += 1
    game['last_throw_time'] = datetime.utcnow()
    me['is_new'] = False
    
  # USER ACTIONS LOG
  app_tables.user_actions.add_row(user=me, action_type='throw', time=datetime.utcnow())
  return {'success': True,
          'add_home': add_home,
          'game': game}


@anvil.server.callable
def get_game(game_id):
  '''
  DEPRECATED all game updates come through get_games()
  
  if user has permissions:
  returns game with id game_id 
  
  args: game id
  returns:
    {'success': bool,
     'game': game (row)}
  '''
  if debug:
    print('get_game (single)')

  me = anvil.server.session.get('me', False)
  if not me:
    return {
      'success': False,
      'msg': 'not logged in',
    }
  
  game = app_tables.games.get_by_id(game_id)
  
  if not (game['player_0'] == me or game['player_1'] == me):
    print('attempted to throw in someone elses game')
    return {'success': False, 
            'msg': 'You are not in that game, cheater.'}
  
  else:
    # print(game['has_ball'], ' has the ball')
    return {'success': True,
            'game': game}


@anvil.server.callable
def update_wall(number):
  if debug:
    print('update_wall')

  me = anvil.server.session.get('me', False)
  if not me:
    return {
      'success': False,
      'msg': 'not logged in',
    }
  
  me['wall_throws'] = number
  # me.update(wall_throws=number)
  return {'success': True}


@anvil.server.callable
def update_colors(color1, color2):
  if debug:
    print('update_colors')

  me = anvil.server.session.get('me', False)
  if not me:
    return {
      'success': False,
      'msg': 'not logged in',
    }

  me['color_1'] = '#' + is_valid_color(color1)
  me['color_2'] = '#' + is_valid_color(color2)
  return {'success': True,
          'user': me,}

'''
@anvil.server.callable
def some_connection():
  do_login('5555555555', '5')
  return get_connections().search()[0].get_id()
'''
