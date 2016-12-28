#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""This script creates the BIOWAVE  test database - the small `test`
database with only 20 person's data - in a single pass.
"""

import os
import re

from .models import *


class DatabaseError(Exception):
    def __init__(self, value = 'Database error'):
        self.value = value
    def __str__(self):
        return self.value

def __get_filelist__(filelist_path):
    with open(filelist_path, 'r') as content_file:
        content = content_file.read()
    content = content.split('\n')

    enroll_filelist = set()
    probe_filelist = set()

    for line in content:
        if len(line) > 0:
            splitted_line = line.split(', ')
            if len(splitted_line) == 3:
                enroll_filelist.add(splitted_line[0])
                probe_filelist.add(splitted_line[1])

    enroll_filelist = list(enroll_filelist)
    probe_filelist = list(probe_filelist)

    for k in range(len(enroll_filelist)):
        file_name, _ = os.path.splitext(enroll_filelist[k])
        if file_name.startswith("../Database_jpg_90/"):
            file_name = file_name[19:]
        enroll_filelist[k] = file_name

    for k in range(len(probe_filelist)):
        file_name, _ = os.path.splitext(probe_filelist[k])
        if file_name.startswith("../Database_jpg_90/"):
            file_name = file_name[19:]
        probe_filelist[k] = file_name

    return enroll_filelist, probe_filelist

def __test_filelist_for_dublicates__(list_a, list_b):
    bad = 0
    for item in list_a:
        if list_a in list_b:
            bad = bad + 1
    return bad



def add_clients(session, imagedir, verbose):
  """
  Add clients to the BIOWAVE_TEST database.

  Similarly as in the BIOWAVE database, in the BIOWAVE_TEST database it is assumed
  that each person's hand (Left / Right) is a different client.

  To add cleints, script looks in each person's hand subfolders (Left / Right),
  if they exist, and contains images, hand (a client) is added to the database.

  The Database home dir is defined by the variable "imagedir".
  """
  # get the persons, "listdir" excludes the special entries:
  person_folder_list = os.listdir(imagedir)
  # sort the person list so that order always is the same:
  person_folder_list.sort()
  for person in person_folder_list:
      try:
          original_client_id = int(re.findall("\d+[\.]?\d*", person)[0])
      except:
          raise DatabaseError("Person folder name isn't in an correct form - Person_X or Person X, where X - id - folder's name is - {}".format(person))
      person_hand_folder_path = os.path.join(imagedir, person)
      person_hand_folders = os.listdir(person_hand_folder_path)
      person_hand_folders.sort()
      for person_hand in person_hand_folders:
          person_hand_session_folder_path = os.path.join(person_hand_folder_path, person_hand)
          person_hand_images = os.listdir(person_hand_session_folder_path)
          person_hand_images = filter(lambda image: image.endswith(".png") == True, person_hand_images)
          person_hand_images = list(set(person_hand_images))
          person_hand_images.sort()
          if len(person_hand_images) >= 5:
              if person_hand.startswith("R") == True:
                  hand = "R"
              elif person_hand.startswith("L") == True:
                  hand = "L"
              else:
                  raise DatabaseError("Person' s hand folder - {} - don't starts with 'R' or 'L', aborting operation".format(person_hand))
              if verbose>1: print("  Adding client, client's information:\nOriginal client ID = {}, hand = {}".format(original_client_id, hand))
              # ADD CLIENT:
              session.add(Client(original_client_id, hand))
              # AD CLIENT'S FILES THERE:
              # To do so, first commit the session so that we can read the user SQL ID:
              # ADD ALL FILES FOR PARTICULAR CLIENT (relationship - client SQL ID)
              session.commit()
              c = session.query(Client).filter(Client.original_client_id == original_client_id).filter(Client.hand == hand).first()

              for nr, image in enumerate(person_hand_images, start=1):
                  image_full_path = os.path.join(person_hand_session_folder_path, image)
                  image_short_path = os.path.relpath(image_full_path, imagedir)
                  image_short_path, _ = os.path.splitext(image_short_path)
                  if verbose>1: print("    Adding file '{}'...".format(image_short_path))
                  M = session.query(File).filter(File.model_id == "c_{}_i_{}".format(c.id,nr)).first()
                  if M:
                      raise DatabaseError("\n\nAlready exist file's with such MODEL_ID. Possibly SQL database already exist. Please try using command:\n\n     ./bin/bob_dbmanage.py database_test create -R \n")
                  else:
                      session.add(File(c.id, image_short_path, nr))


def add_protocols(session, devfile, evalfile, verbose):
  """
    Adds protocols

    BIOWAVE_TEST database has only a single protocol - "all". It has purposes:
      dev - enroll;
      dev - probe;
      eval - enroll;
      eval - probe.

  Clients are added to these protocols using provided text files. If files for \
  any of the above listed porpuses doubles with different porpuse file, an error
  is rised.

  """
  dev_enroll, dev_probe     = __get_filelist__(devfile)
  bad = __test_filelist_for_dublicates__(dev_enroll, dev_probe)
  if bad != 0:
      raise DatabaseError("Doubling {} database dev / enroll and dev / probe files, aborting building database protocols.".format(bad))

  eval_enroll, eval_probe    =  __get_filelist__(evalfile)
  bad = __test_filelist_for_dublicates__(eval_enroll, eval_probe)
  if bad != 0:
      raise DatabaseError("Doubling {} database eval / enroll and eval / probe files, aborting building database protocols.".format(bad))

  # test all dev / eval protocol combinations:
  bad =       __test_filelist_for_dublicates__(dev_enroll, eval_enroll)
  bad = bad + __test_filelist_for_dublicates__(dev_enroll, eval_probe)

  bad = bad + __test_filelist_for_dublicates__(dev_probe, eval_enroll)
  bad = bad + __test_filelist_for_dublicates__(dev_probe, eval_probe)
  if bad != 0:
      raise DatabaseError("Doubling {} files between dev / eval filelists, aborting building database protocols.".format(bad))
  protocol_person_definitions = {}
  protocol_person_definitions['all'] = [dev_enroll, dev_probe, eval_enroll, eval_probe]
  # 2. ADDITIONS TO THE SQL DATABASE
  protocolPurpose_list = [('dev', 'enroll'), ('dev', 'probe'), ('eval', 'enroll'), ('eval', 'probe')]
  for proto in protocol_person_definitions:
    current_protocol = Protocol(proto)
    # Add protocol
    if verbose:
        print("Adding protocol %s..." % (proto))
    session.add(current_protocol)
    session.flush()
    session.refresh(current_protocol)
    # Add protocol purposes
    for key in range(len(protocolPurpose_list)):
      purpose = protocolPurpose_list[key]
      #print(purpose)
      if verbose > 1:
          print("  Adding protocol purpose ('%s','%s')..." % (purpose[0], purpose[1]))
      prot_purp = ProtocolPurpose(current_protocol.id, purpose[0], purpose[1])
      session.add(prot_purp)
      session.flush()
      session.refresh(prot_purp)

      files_to_add = protocol_person_definitions[proto][key]
      for file_to_add in files_to_add:
          print(file_to_add)
          try:
              f = session.query(File).filter(File.path == file_to_add).one()
          except MultipleResultsFound:
              raise DatabaseError("Multiple files correspond to a single dev / eval file list entry, aborting building database protocols.")
          if verbose > 1:
            print("    Adding to the protocol Client's {} file {}...".format(f.client_id, f.path))

          # adding file to the protocol purpose:
          prot_purp.files.append(f)

  session.commit()


def create_tables(args):
  """Creates all necessary tables (only to be used at the first time)"""

  from bob.db.base.utils import create_engine_try_nolock
  engine = create_engine_try_nolock(args.type, args.files[0], echo=(args.verbose > 2))
  Base.metadata.create_all(engine)

# Driver API
# ==========

def create(args):
  """Creates or re-creates this database"""

  from bob.db.base.utils import session_try_nolock

  dbfile = args.files[0]

  if args.recreate:
    if args.verbose and os.path.exists(dbfile):
      print('unlinking %s...' % dbfile)
    if os.path.exists(dbfile): os.unlink(dbfile)

  if not os.path.exists(os.path.dirname(dbfile)):
    os.makedirs(os.path.dirname(dbfile))

  # ALL THE WORK:
  #----------------------------------------------------------------------------
  create_tables(args)
  s = session_try_nolock(args.type, dbfile, echo=(args.verbose > 2))
  add_clients(s, args.imagedir, args.verbose)

  #add_annotations(s, args.annotdir, args.verbose)
  #add_protocols(s, args)


  add_protocols(s, args.devfile, args.evalfile, args.verbose)

  s.commit()
  s.close()


def add_command(subparsers):
  """Add specific subcommands that the action "create" can use"""

  parser = subparsers.add_parser('create', help=create.__doc__)

  parser.add_argument('-R', '--recreate', action='store_true', help="If set, I'll first erase the current database")
  parser.add_argument('-v', '--verbose', action='count', help="Do SQL operations in a verbose way?")
  parser.add_argument('-D', '--imagedir', metavar='DIR', default='/idiap/project/biowave/biowave_test/database/', help="Change the relative path to the directory containing the images of the BIOWAVE database.")
  parser.add_argument('-e', '--evalfile', metavar='DIR', default='/idiap/project/biowave/biowave_test/evalSetGenuine.txt', help="Change the path and file name containing the evaluate group's file list of the BIOWAVE_TEST database (defaults to %(default)s)")
  parser.add_argument('-d', '--devfile', metavar='DIR', default='/idiap/project/biowave/biowave_test/devSetGenuine.txt', help="Change the path and file name containing the develop group's file list of the BIOWAVE_TEST database (defaults to %(default)s)")

  parser.set_defaults(func=create) #action
