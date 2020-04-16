import argparse
import re
import os
import glob
from pprint import pprint
from types import SimpleNamespace

from mgz.summary import Summary

parser = argparse.ArgumentParser(description='Analyze AOE DE games.')
parser.add_argument('--dir',
                    nargs='?',
                    default='C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame',
                    help='folder to find saved games')
args = parser.parse_args()

files = glob.glob(f'{args.dir}/**/*.aoe2record', recursive=True)

files.sort(key=os.path.getmtime)
files.reverse()

# Most don't work. This does.
# files = ['C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.11 193658 (2).aoe2record']

# the only working files.
# files=[
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

def load_game(f):
  with open(f, 'rb') as data:
    try:
      s = Summary(data)
      error = None
      header = s.get_header()
      del header['map_info'] # tons of data that isn't needed.
    except Exception as e:
      s = None
      error = str(e)

    re_result = re.match('.*Replay v([0-9.]+).*', f)
    if re_result:
      version = re_result[1]
    else:
      version = None
    
    if error:
      print(error, '| path:', f)
    
    return {
      'path': f,
      'time': os.path.getmtime(f),
      'version': version,
      'header': s and s.get_header(),
      'players': s and s.get_players(),
      'error': error
    }


def count_by(objs, fn):
  for obj in objs:
    key = fn(obj)
    print(key)


all_games = [load_game(f) for f in files]
games = [g for g in all_games if g['error'] is None]
errored_games = [g for g in all_games if g['error'] is not None]

# Error debugging.

games_by_version = {}
for game in all_games:
  key = game['version']
  if key not in games_by_version:
    games_by_version[key] = []
  games_by_version[key].append(game)


print(f'{len(games)} / {len(files)} parsed without errors\n')
for version, games in dict(sorted(games_by_version.items())).items():
  count = len(games)
  games_with_errors = [g for g in games if g['error'] is not None]
  print(f'Version {version} ({count - len(games_with_errors)} / {count}) parsed without errors')
  for game in games_with_errors:
    print('\t' , game['error'].replace('\n', ' '))
print()

# Fun stats.

lighthouse_players = ['Hoten', 'paulie__b', 'Whiskey', 'blarp7070', 'MikeB924', 'jazyan11']
def is_lighthouse_game(game):
  return len([1 for p in game['players'] if p['name'] in lighthouse_players]) >= 2
lighthouse_games = [g for g in games if is_lighthouse_game(g)]

def count_by(games, fn):
  counts = {}
  for g in games:
    results = fn(g)
    if not isinstance(results, list):
      results = [results]
    for result in results:
      if result not in counts:
        counts[result] = 0
      counts[result] += 1
  return counts

def show(name, fn):
  print(f'=== {name}')
  counts = count_by(lighthouse_games, fn)
  counts = {k: v for k, v in sorted(counts.items(), key=lambda item: -item[1])}
  for k, v in counts.items():
    print(f'  {k}: {v}')
  
  print()

show('winners',     lambda game: [p['name'] for p in game['players'] if p['winner']])
show('game types',  lambda game: game['header'].lobby.game_type)
show('lobby',       lambda game: game['header'].de.lobby_name.value)
