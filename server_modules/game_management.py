import anvil.secrets
import anvil.users
import tables
from tables import app_tables
import anvil.server

from utils import is_valid_number, hash_phone, generate_code
from twilio_auth import send_authorization_message

from datetime import datetime
debug = True


@anvil.server.callable
def add_connection(phone):
  '''
  adds a connection to graph from current logged in to user with phone number
  user ('me') is player 0, other_user is player 1
  
  args:
    phone: other_user's phone number
    
  returns:
    {'success': bool,
     'enabled': bool,
     'msg': status description,
     'game': game (row reference),}
  '''
  me = anvil.server.session.get('me', False)
  if not me:
    return {
      'success': False,
      'msg': 'not logged in',
    }
  
  other_user = app_tables.users.get(phone_hash=hash_phone(phone))
  if not other_user:
    return {
      'success': False,
      'msg': 'other player did not have an account',
    }
  
  if other_user['handle']:
    # print('add connection to', other_user['handle'])
    pass
  else:
    pass
    # print('add hypothetical connection to {}'.format(phone))
    
  my_games = get_games(server=True)  # get a dict of games by id

  # protect whole operation from simultaneous adding
  with tables.Transaction() as txn:
    # search for pre-existing games
    
    for _id, game in my_games.items():
      if game['player_1'] == other_user or game['player_0'] == other_user:
        
        # success is not really True, but same result
        return {
          'success': True,
          'enabled': row['game']['p1_enabled'],
          'msg': 'game already exists',
          'game': row['game'],}
    
    # no existing connection; make one
    game = app_tables.games.add_row(
      connection_time=datetime.utcnow(),
      is_active=False,
      player_0=me,
      player_1=other_user,
      p1_enabled=other_user['enabled'],
      throws=other_user['enabled'] - 2,
      last_throw_time=datetime.utcnow(),)
          
    return {'success': True,
            'enabled': game['p1_enabled'],
            'msg': 'new game created',
            'game': game,}


@anvil.server.callable
def get_games(server=False):
  '''
  get all the connections for current user
  
  returns {'success': bool,
           'msg': status message,
           'order': list of game ids in order
           'games': {game_id: game},}
  '''
  if debug:
    print('get_games (all)')
    
  me = anvil.server.session.get('me', False)
  if not me:
    return {
      'success': False,
      'msg': 'not logged in',
    }
   
  else:
    games = {}
    order = []
    waiting = []
    for game in app_tables.games.search(tables.order_by('throws', ascending=False)):
      if game['player_0'] == me or game['player_1'] == me:
        _id = game.get_id()
        if not game['p1_enabled']:
          waiting.append(_id)
        else:
          order.append(_id)
        games[_id] = game
    
    order += waiting
    assert len(order) == len(games)
    
    if server:
      return games
    
    return {'success': True,
            'msg': 'retreived {} games'.format(len(games)),
            'order': order,
            'wall_throws': me['wall_throws'],
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
    print('throw')
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

  print('setting:')
  with tables.Transaction() as txn:

    game['has_ball'] = abs(1 - game['has_ball'])  # flip who has ball
    game['throws'] += 1
    game['last_throw_time'] = datetime.utcnow()

  print('set')
  return {'success': True,
          'game': game}


@anvil.server.callable
def get_game(game_id):
  '''
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
            'msg': 'You are not in that game.'}
  
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

  me['color_1'] = color1
  me['color_2'] = color2
  return {'success': True,
          'user': me,}

'''
@anvil.server.callable
def some_connection():
  do_login('5555555555', '5')
  return get_connections().search()[0].get_id()
'''