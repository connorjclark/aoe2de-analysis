import os
import glob
from pprint import pprint
from types import SimpleNamespace

from mgz.summary import Summary

save_dir = 'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame'
files = glob.glob(f'{save_dir}/**/*.aoe2record', recursive=True)

files.sort(key=os.path.getmtime)
files.reverse()

# Most don't work. This does.
# files = ['C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.11 193658 (2).aoe2record']

# the only working files.
files=[
  'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.16 224255 (4).aoe2record',
  'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.16 223211 (4).aoe2record',
  'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.16 222642 (4).aoe2record',
  'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.16 220410 (2).aoe2record',
  'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.16 213423 (4).aoe2record',
  'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.16 211520 (4).aoe2record',
  'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.11 221130 (2).aoe2record',
  'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.11 193658 (2).aoe2record',
  'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.09 213841 (3).aoe2record',
  'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.09 205818 (2).aoe2record',
  'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.09 203848 (2).aoe2record',
  'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.07 144321 (2).aoe2record',
  'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.07 133442 (2).aoe2record',
  'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.06 234216 (3).aoe2record',
  'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.06 231420 (3).aoe2record',
  'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.06 222325 (4).aoe2record',
  'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.06 221747 (4).aoe2record',
  'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.06 221542 (2).aoe2record',
  'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.06 202338 (2).aoe2record',
  'C:/Users/Connor/games/Age of Empires 2 DE/76561198009093901/savegame\MP Replay v101.101.35584.0 @2020.03.06 201515 (2).aoe2record',
]

def load_game(f):
  with open(f, 'rb') as data:
    s = Summary(data)
    
    header = s.get_header()
    del header['map_info'] # tons of data that isn't needed.
    
    return {
      'header': s.get_header(),
      'players': s.get_players(),
    }


def load_games(files):
  games = []
  for f in files:
    try:
      game = load_game(f)
      games.append(game)
    except Exception as e:
      # print(f)
      # print(e)
      pass
  return games

def count_by(objs, fn):
  for obj in objs:
    key = fn(obj)
    print(key)


games = load_games(files)

winners = {}
for game in games:
  for p in game['players']:
    if p['winner']:
      key = p['name'] 
      if key not in winners:
        winners[key] = 0
      winners[key] += 1


game_types = {}
for game in games:
  key = game['header']['lobby']['game_type']
  if key not in game_types:
    game_types[key] = 0
  game_types[key] += 1

  
print(f'{len(games)} / {len(files)} parsed without errors\n')

print('=== game types')
pprint(game_types)
print()

print('=== winners')
pprint(winners)
print()
