import argparse
import re
import os
import glob
import simplejson as json
from collections import namedtuple
from pprint import pprint
from types import SimpleNamespace
from collections.abc import Iterable

from mgz.summary import Summary

parser = argparse.ArgumentParser(description='Analyze AOE DE games.')
parser.add_argument('--dir',
                    nargs='?',
                    default='C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame',
                    help='folder to find saved games')
parser.add_argument('--nocache',
                    action='store_true',
                    default=False)
parser.add_argument('--rmerrors',
                    action='store_true',
                    default=False)
args = parser.parse_args()

files = glob.glob(f'{args.dir}/**/*.aoe2record', recursive=True)

files.sort(key=os.path.getmtime)
files.reverse()

# Most don't work. This does.
# files = ['C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.11 193658 (2).aoe2record']

# many working files.
# files=[
#   'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame/MP Replay v101.101.36202.0 @2020.04.17 222240 (3).aoe2record',
#   'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.16 224255 (4).aoe2record',
#   'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.16 223211 (4).aoe2record',
#   'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.16 222642 (4).aoe2record',
#   'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.16 220410 (2).aoe2record',
#   'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.16 213423 (4).aoe2record',
#   'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.16 211520 (4).aoe2record',
#   'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.11 221130 (2).aoe2record',
#   'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.11 193658 (2).aoe2record',
#   'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.09 213841 (3).aoe2record',
#   'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.09 205818 (2).aoe2record',
#   'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.09 203848 (2).aoe2record',
#   'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.07 144321 (2).aoe2record',
#   'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.07 133442 (2).aoe2record',
#   'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.06 234216 (3).aoe2record',
#   'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.06 231420 (3).aoe2record',
#   'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.06 222325 (4).aoe2record',
#   'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.06 221747 (4).aoe2record',
#   'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.06 221542 (2).aoe2record',
#   'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.06 202338 (2).aoe2record',
#   'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.06 201515 (2).aoe2record',
# ]

def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())
def json2obj(data): return json.loads(data, object_hook=_json_object_hook)

def get_cache_path(f):
  return f'{os.path.dirname(os.path.abspath(__file__))}/.cache/{os.path.basename(f)}.json'

# Parsing game data takes a long time, so a summary of the game is cached.
def load_game_from_cache(f):
  if args.nocache:
    return

  summary_path = get_cache_path(f)
  if not os.path.exists(summary_path):
    return

  with open(summary_path) as file:
    game = json2obj(file.read())

  # Retry parsing the game if there was an error.
  # Use this arg when updating aoc_mgz
  if args.rmerrors and game.error is not None:
    os.remove(summary_path)
    return

  return game

def load_game(f):
  summary, error = _load_game(f)
  
  re_result = re.match('.*Replay v([0-9.]+).*', f)
  if re_result:
    version = re_result[1]
  else:
    version = None
  
  header = summary and summary.get_header()
  players = summary and summary.get_players()
  lobby = header and header.lobby
  de = header and header.de
  restored = header and header.initial.restore_time > 0
  
  if players:
    for i, ach in enumerate(header.ach):
      players[i]['achievements'] = ach

  if lobby:
    del lobby.messages
  if de:
    del de.players
    del de.strings
    del de.strategic_numbers
    del de.guid

    for k in de:
      if isinstance(de[k], Iterable) and 'length' in de[k] and 'value' in de[k] and isinstance(de[k].value, bytes):
        de[k] = str(de[k].value, 'utf8')
  
  game = {
    'de': de,
    'error': error,
    'lobby': lobby,
    'path': f,
    'players': players,
    'restored': restored,
    'time': os.path.getmtime(f),
    'version': version,
    'duration': summary.get_duration() if summary else 0,
  }
  
  with open(get_cache_path(f), 'w') as file:
    json_str = json.dumps(game, indent=2)
    file.write(json_str)
    return json2obj(json_str)


def _load_game(f):
  with open(f, 'rb') as data:
    try:
      summary = Summary(data)
      error = None
    except Exception as e:
      summary = None
      error = str(e)
    
    if error:
      print(error, '| path:', f)
    
    return summary, error


def count_by(objs, fn):
  for obj in objs:
    key = fn(obj)
    print(key)


all_games = []
games_to_load = []
for f in files:
  game = load_game_from_cache(f)
  if game:
    all_games.append(game)
  else:
    games_to_load.append(f)

for i, f in enumerate(games_to_load):
  print(f'{i+1} / {len(games_to_load)} {f}')
  all_games.append(load_game(f))

ok_games = [g for g in all_games if g.error is None]
errored_games = [g for g in all_games if g.error is not None]

# Error debugging.

games_by_version = {}
for game in all_games:
  if game.version:
    key = game.version
  else:
    key = 'unknown'
  if key not in games_by_version:
    games_by_version[key] = []
  games_by_version[key].append(game)


print(f'{len(ok_games)} / {len(files)} parsed without errors\n')
for version, games in dict(sorted(games_by_version.items())).items():
  count = len(games)
  games_with_errors = [g for g in games if g.error is not None]
  print(f'Version {version} ({count - len(games_with_errors)} / {count}) parsed without errors')
  for game in games_with_errors:
    print('\t' , game.error.replace('\n', ' '))
print()

# Fun stats.

lighthouse_players = ['Hoten', 'paulie__b', 'paulieblueeyes', 'Whiskey', 'blarp7070', 'MikeB924', 'jazyan11', 'rdiscount', 'Casper', '[V101]Ursor']
def is_lighthouse_game(game):
  if game.restored or game.players is None:
    return False
  return len([1 for p in game.players if p.name in lighthouse_players]) >= 2
lighthouse_games = [g for g in ok_games if is_lighthouse_game(g)]


def aggregate(games, group_by_fn, reduce_fn):
  results = {}

  for g in games:
    # Can have multiple groups (ex: multiple winners)
    groups = group_by_fn(g)
    if not isinstance(groups, list):
      groups = [groups]
    
    for group in groups:
      if group not in results:
        results[group] = None
      results[group] = reduce_fn(results[group] or 0, group, g)

  return results


def count_reducer(acc, group, game):
  return acc + 1

def resource_reducer(key):
  def reducer(acc, group, game):
    player = next(p for p in game.players if p.name == group)
    cur = getattr(player.achievements, key)
    return acc + cur
  return reducer


def show(name, group_by_fn, reduce_fn=count_reducer):
  print(f'=== {name}')
  results = aggregate(lighthouse_games, group_by_fn, reduce_fn)
  results = {k: v for k, v in sorted(results.items(), key=lambda item: -item[1])}
  for k, v in results.items():
    try:
      print(f'  {k}: {v}')
    except:
      k = k.encode('utf-8')
      print(f'  {k}: {v}')
  
  print()

  
for i, game in enumerate(ok_games):
  print(i, [p.name for p in game.players if p.winner])

show('winners',     lambda game: [p.name for p in game.players if p.winner])
# Not sure what unit "duration" is ...
# show('time played (hours?)', lambda game: [p.name for p in game.players], lambda acc, group, game: acc + (game.duration if 'duration' in game else 0) / 1000 / 60 / 60)

# Achievements don't work yet.
# show('food',        lambda game: [p.name for p in game.players], resource_reducer('total_food'))
# show('wood',        lambda game: [p.name for p in game.players], resource_reducer('total_wood'))
# show('gold',        lambda game: [p.name for p in game.players], resource_reducer('total_gold'))
# show('stone',       lambda game: [p.name for p in game.players], resource_reducer('total_stone'))
show('game types',  lambda game: game.lobby.game_type)
show('lobby',       lambda game: game.de.lobby_name)

# Total time played?
