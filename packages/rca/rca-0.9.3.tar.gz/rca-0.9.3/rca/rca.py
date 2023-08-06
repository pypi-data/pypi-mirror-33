#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Recompress Audio: a configuration-driven audio recompression utility
Copyright (C) 2018 Kevin R Croft

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__name__ = "rca"
__version__ = "0.9.3"

# Check if we're running Python 3.5+
import sys
if (sys.version_info) < (3, 5):
    print("CRITICAL: this script requires at least Python 3.5")
    sys.exit(1)

# Built-in modules
import os
import yaml
import logging
import subprocess
from shutil import copy2
from fnmatch import fnmatch
from multiprocessing.dummy import Pool as ThreadPool

# Third-party module: appdirs, determines where RCA's config files should go on OSX, Windows, and Linux
try: from appdirs import user_data_dir
except ImportError:
  print('CRITICAL: this script requires the appdirs module, install it with "sudo pip3 install appdirs"')
  sys.exit(1)

# Pull in own relative Track class
from .track import Track

# Setup the logger
module = sys.modules['__main__'].__file__
log = logging.getLogger(module)

def parse():
  import argparse

  parser = argparse.ArgumentParser(
    description='Conditionally (re)encode tracks using the specified codec')

  parser.add_argument("--version", action="version",
                      version="{} {}".format(__name__, __version__))

  parser.add_argument("-v", "--verbose", dest="verbose_count",
                      action="count", default=0,
                      help="increases log verbosity for each occurence.")

  default_config_dir=user_data_dir('rca', 'Kevin R Croft')
  parser.add_argument(
    '-d', '--config_dir',
    default=default_config_dir,
    help='Use a different config directory. Default is ' + default_config_dir)

  default_track_type='wav'
  parser.add_argument(
    '-t', '--track_type',
    default=default_track_type,
    help='Use a different source track type (ie: flac). Default is ' + default_track_type)

  parser.add_argument(
    'codec',
    metavar='CODEC',
    help='Set the codec to type, ie: opus, vorbis, aac, he-aac, he-aac-v2, mp3')

  del argparse
  return parser.parse_args()


def get_codecs(config_dir):
  codecs = []
  if os.path.isdir(config_dir):
    for name in os.listdir(config_dir):
      codec_path = os.path.join(config_dir, name)
      if os.path.isfile(codec_path) and fnmatch(name, '*-profiles.yml'):
        codecs.append(name.replace('-profiles.yml', ''))
        log.info('found codec profiles: ' + codec_path)
  return codecs


def initialize_config_dir(config_dir):
  os.makedirs(config_dir, exist_ok=True)
  script_path, script_name = os.path.split(os.path.realpath(__file__))
  source_dir = os.path.join(script_path, 'config')
  if os.path.isdir(source_dir):
    for source in os.listdir(source_dir):
      source_path = os.path.join(source_dir, source)
      if os.path.isfile(source_path) and fnmatch(source, '*.yml'):
        target_path = os.path.join(config_dir, source)
        if not os.path.exists(target_path):
          log.info('writing initial config: ' + target_path)
          copy2(source_path, target_path)
        else:
          log.info('using existing config: ' + target_path)

        target_dist_path = target_path + '.dist'
        if (not os.path.exists(target_dist_path) or
           os.path.getmtime(source_path) > os.path.getmtime(target_dist_path)):
          log.info('writing new distribution config: ' + target_dist_path)
          copy2(source_path, target_dist_path)
        else:
          log.info('found existing distribution config: ' + target_dist_path)
  else:
    log.error('missing source config path: ' + source_dir)

def get_tracks(track_type, defaults):
  tracks = dict()
  for f in os.listdir('.'):
    if os.path.isfile(f) and fnmatch(f, '*.' + track_type):
      t = Track(f, defaults.copy() )
      tracks[t.n] = t
      log.info('found track: ' + t.basename)

  return tracks

def in_range(_range):
  matches=[]
  pprev=False
  prev=False

  for i in _range:
    if isinstance(i, int):
      i = int(i)
      matches.append(i)

      # scenarios: [1, -, 4, -, 6]
      if isinstance(pprev, int) and prev == '-':
        for n in range(pprev + 1, i):
          matches.append(n)

    pprev = prev
    prev = i

  return matches

def poulate_tier2(info, mprop):
  for key in info:
    if key in mprop['tier2']:
      for property, values in mprop['values'].items():
        if key in values:
          info[key][property] = key
          break

def poulate_track_properties(tracks, mprop):
  filename = 'properties.yml'
  if os.path.isfile(filename):
    with open(filename) as info_file:
      info = yaml.load(info_file)

      poulate_tier2(info, mprop)

      for key in info:
        if key in mprop['tier1']:
          [tracks[t].apply_properties(info[key]) for t in tracks]
          log.debug('applying {} properties to all tracks'.format(key) )
          break

      for key in info:
        if key in mprop['tier2']:
          selected = tracks
          if 'range' in info[key]:
            selected = in_range(info[key].pop('range'))
          log.debug('applying {} properties to tracks {}'.format(key, ', '.join([str(t) for t in selected])))
          [tracks[t].apply_properties(info[key]) for t in selected]

      for key in info:
        if key not in mprop['tier1'] and key not in mprop['tier2']:
          for t in tracks:
            if key == tracks[t].basename:
              log.debug('applying {} properties individually'.format(key))
              tracks[t].apply_properties(info[key])

  else:
    log.warn('track information file {} not found in current directory'.format(filename))

# Get version from command line
def get_version(app, version_arg):
    version=None
    raw_output = subprocess.check_output([app, version_arg], stderr=subprocess.STDOUT)
    for line in raw_output.splitlines():
      line = line.strip().decode('ascii', 'ignore')
      # take the first line having a number and a dot, otherwise move onto the next line
      if '.' in line and any(str(char).isdigit() for char in line):
        version = line
        break

    if not version:
      log.error('could not find version from {} {} in output {}'.format(app, version_arg, raw_output))

    return version

# Determine and populate the tracks with the specified codec options given the track properties
def populate_track_desired_encoding(tracks, mprop, config_dir, codec):
  codec_app=None
  codec_ver=None
  inout_args=None

  filename = os.path.join(config_dir, '{}-profiles.yml'.format(codec))

  if os.path.isfile(filename):
    with open(filename) as codec_file:
      codec = yaml.load(codec_file)
      codec_app = codec['application']
      codec_ver = get_version(codec_app, codec['version_arg'])
      inout_args = codec['inout_args']
      log.info('loaded codec profiles from: ' + filename)
      log.info('determined {} version: {}'.format(codec_app, codec_ver))

      for t in tracks:
        track = tracks[t]
        track_properties = track.properties_as_str(mprop['order'])
        if track_properties in codec['combinations']:
          track.desired_options = codec['combinations'][track_properties]
          log.debug('setting track {} desired encode options to: {}'.format(t, track.desired_options))

        else:
          log.critical('no profile exists for properties "{}" in codec file "{}"'.format(track_properties, filename))
  else:
    log.warn('codec file {} not found. Available codecs are: {}'.format(filename, ', '.join(get_codecs(config_dir))) )

  return codec_app, codec_ver, inout_args

# Populate the current encoding options from encoding.yml
def populate_track_actual_encoding(tracks, codec):
  encoding_app=None
  encoding_ver=None

  filename = '{}-encoding.yml'.format(codec)
  if os.path.isfile(filename):
    with open(filename) as encoding_file:
      encoding = yaml.load(encoding_file)
      encoding_app = encoding['application']
      encoding_ver = encoding['version']

      log.info('loaded existing encoding settings from: ' + filename)
      log.info('tracks were previously encoded with {} version: {}'.format(encoding_app, encoding_ver))

      for n in tracks:
        name = tracks[n].basename
        if name in encoding:
          tracks[n].actual_options = encoding[name]
          log.debug('setting track {} actual encode options to: {}'.format(n, encoding[name]))

  return encoding_app, encoding_ver

def save_encoding(tracks, codec, desired_app, desired_ver, results):
  output = {}
  output['application'] = desired_app
  output['version'] = desired_ver
  recoded_list = [t for t, rcode in results]

  for t in tracks:
    if t not in recoded_list:
      output[tracks[t].basename] = tracks[t].actual_options

  for t, succeeded in results:
    if succeeded:
      output[tracks[t].basename] = tracks[t].desired_options
    else:
      output[tracks[t].basename] = 'failed'

  filename = '{}-encoding.yml'.format(codec)
  with open(filename, 'w') as encoding_file:
    yaml.dump(output, encoding_file, default_flow_style=False)
    log.info('saved encoding settings to: ' + filename)


# Define a callable to do the work. It should take one work item.
def encoder(cmd_args):

  # guilty until proven good
  rcode=False

  # the first item is the track number, which we pop-off and return with the result
  track_number = cmd_args.pop(0)

  # run it
  try:
    completed = subprocess.run(cmd_args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

  except subprocess.CalledProcessError as err:
    log.error(err)
  else:
    log.debug('return code for track {}:'.format(track_number, completed.returncode))
    log.info('output for track {}: {!r}'.format(track_number, completed.stdout))
    log.info('stderr for track {}: {!r}'.format(track_number, completed.stderr))

    if completed.returncode == 0:
      rcode=True

  return (track_number, rcode)

def recode(tracks, selected, desired_app, inout_args):
  queue = []
  results = []
  for t in selected:
    encode_args = [t, 'echo', desired_app]
    encode_args.extend(tracks[t].desired_options.split())
    inout_str = inout_args.format(infile=tracks[t].filename, outfile=tracks[t].basename)
    encode_args.extend(inout_str.split())
    queue.append(encode_args)

  with ThreadPool(os.cpu_count()) as pool:
    results = pool.map(encoder, queue)

  return results

def load_master_properties(config_dir):
  filename = os.path.join(config_dir, 'master_properties.yml')
  if os.path.isfile(filename):
    with open(filename) as info_file:
      return yaml.load(info_file)
  else:
    log.critical('cannot find master properties file "{}"'.format(filename))

def main():
  rcode = 1

  args = parse()

  # Set log level to WARN going more verbose for each new -v.
  log.setLevel(max(3 - args.verbose_count, 0) * 10)

  logging.basicConfig(stream=sys.stderr, level=logging.DEBUG,
                      format='%(levelname)s: %(message)s')

  log.info("Executing Recompress Audio (RCA) version %s" % __version__)

  initialize_config_dir(args.config_dir)

  mprop = load_master_properties(args.config_dir)

  # Fetch the current track filenames
  tracks = get_tracks(args.track_type, mprop['defaults'])
  if not tracks:
    log.warning('*.{} files were not found in the current directory'.format(args.track_type))

  # populate each track with its property info
  poulate_track_properties(tracks, mprop)

  # populate track with desired encoding options
  desired_app, desired_ver, inout_args = populate_track_desired_encoding(tracks, mprop, args.config_dir, args.codec)

  # populate track with actual encoding options, if the files have already been encoded
  actual_app, actual_ver = populate_track_actual_encoding(tracks, args.codec)

  # determine which tracks need re-encoding
  selected = [t for t in tracks]
  if actual_app == desired_app and actual_ver == desired_ver:
    selected = [t for t in tracks if tracks[t].actual_options != tracks[t].desired_options]

  # if we need to encode one or more tracks ...
  if selected:
    try:
      results = recode(tracks, selected, desired_app, inout_args)
      log.info(results)
      save_encoding(tracks, args.codec, desired_app, desired_ver, results)
    except KeyboardInterrupt:
        log.critical('Program interrupted!')

  # Stop logging
  logging.shutdown()

