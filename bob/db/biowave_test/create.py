#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Teodors Eglitis <teodors.eglitis@idiap.ch>
#
# Copyright (C) 2011-2016 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

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

#def __get_info_from_file__(path):
#    """
#    function, that returns parameters from the file path.
#    Careful -- no file extension!
#    
#    Example:
#    path = "/idiap/home/teglitis/Desktop/Database/biowave/Person 004/Left/S01/A01/004_M_L_S01_A01_1"
#    
#    [client, gender, hand, session, attempt, image_no] =\
#    __get_info_from_file__(path)
#    
#    print("client = {}, gender = {}, hand = {}, session = {}, attempt = {},\
#    image_no = {}". format(client, gender, hand, session, attempt, image_no))
#    """
#    import re
#    filename = os.path.basename(path)
#    filename = filename.split("_")
#    original_client_id = int(filename[0])
#    gender = (filename[1])
#    hand   = (filename[2])
#    session = int(re.findall("[-+]?\d+[\.]?\d*", filename[3])[0])
#    attempt = int(re.findall("[-+]?\d+[\.]?\d*", filename[4])[0])
#    image_no = int(filename[5])
#    return original_client_id, gender, hand, session, attempt, image_no
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

              for image in person_hand_images:
                  image_full_path = os.path.join(person_hand_session_folder_path, image)
                  image_short_path = os.path.relpath(image_full_path, imagedir)
                  image_short_path, _ = os.path.splitext(image_short_path)
                  if verbose>1: print("    Adding file '{}'...".format(image_short_path))                
                  session.add(File(c.id, image_short_path))
                  
#def add_annotations(session, annotdir, verbose):
#  """
#  Reads annotation files of the BIOWAVE database and stores the annotations in the sql database.
#  All annotation files must be located in the annotdir
#  WITH THE SAME FILE STRUCTURE AS FOR THE ORIGINAL DATABASE.  
#  """
#  def annotate_file(session, file_path):
#      if file_path.endswith('_annotation'):
#          file_path_short = file_path[:-11]
#      f_id = session.query(File.id).filter(File.path == file_path_short).first()
#      if f_id == None:
#          raise DatabaseError("Doesn't exist annotation file's original file.\nAnnotation file path -- {}\n File path that was searched -- {}".format(file_path, file_path_short))
#      if verbose>1: print("Adding anotation to file ID {} -- anotations path -- {}".format(f_id[0], file_path))
#      session.add(Annotation(f_id[0], file_path))
#
#  session.flush()
#  file_paths = set()
#  for dir_, _, files in os.walk(annotdir):
#      for fileName in files:
#          relDir = os.path.relpath(dir_, annotdir)
#          if relDir == ".":
#              file_paths.add(os.path.splitext(fileName)[0])
#          else:
#              relFile = os.path.join(relDir, fileName)
#              relFile, _ = os.path.splitext(relFile)
#              file_paths.add(relFile)
#  # no need for set anymore, convert to list:
#  file_paths = list(file_paths)
#  for file_path in file_paths:
#      annotate_file(session, file_path)


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
  #verbose = args.verbose
#  import random
#  # 0 there we devide database in to the subsets.
#  PROC_WORLD_MULT_SES = 50
#  PROC_SMALL_WORLD = 20

#  q1 = session.query(File.client_id, File.session).group_by(File.client_id).group_by(File.session).subquery()
    
#  one_pers_list     = []
#  mult_pers_list    = []
#  
#  for c, count in session.query(q1.c.client_id, q1.c.session).group_by(q1.c.client_id):
#      if int(count) == 1:
#          one_pers_list.append(c)
#      else:
#          mult_pers_list.append(c)
#          
#          
#  
#  random.seed(1)
#  random.shuffle(mult_pers_list)
#  world_dev_pers_list_count = int(round((len(mult_pers_list) * PROC_WORLD_MULT_SES) / 100.))
#  
#  world_dev_pers_list    = mult_pers_list[0:world_dev_pers_list_count]
#  eval_pers_list         = mult_pers_list[world_dev_pers_list_count:]    
#   
#  random.seed(2)
#  random.shuffle(one_pers_list) 
#  
#  small_one_pers_count = int(round((len(one_pers_list) * PROC_SMALL_WORLD) / 100.))
#  small_mult_pers_count = int(round((len(world_dev_pers_list) * PROC_SMALL_WORLD) / 100.))
  
  # 1. DEFINITIONS  
#  protocol_person_definitions = {}
#  world_all     = one_pers_list[0:small_one_pers_count] + world_dev_pers_list[0:small_mult_pers_count]
#  dev_all       = []
#  eval_all      = []
#  protocol_person_definitions['small'] = [world_all, dev_all, eval_all]
  
  #world_all     = one_pers_list[small_one_pers_count:] + world_dev_pers_list[small_mult_pers_count:]
  
  
  
  
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
#      
#      
#      
#      
#      if(key == 0):
#          clients_to_add = protocol_person_definitions[proto][0]
#          for c in clients_to_add:
#              for f in session.query(File).filter(File.client_id == c):
#                  if verbose > 1:
#                      print("    Adding to the protocol Client's {} file {}...".format(f.client_id, f.path))
#                  prot_purp.files.append(f)
#      elif(key == 1 or key == 2):
#          clients_to_add = protocol_person_definitions[proto][1]
#          # to make script more simple, we will add files later
#      elif(key == 3 or key == 4):
#          clients_to_add = protocol_person_definitions[proto][2]
#          # to make script more simple, we will add files later
#          
#      if (key == 1 or key == 3):
#          # adding just 1st session:
#          for c in clients_to_add:
#              for f in session.query(File).filter(File.client_id == c).filter(File.session == 1):
#                  if verbose > 1:
#                      print("    Adding to the protocol Client's {} file {}...".format(f.client_id, f.path))
#                  prot_purp.files.append(f)
#      elif (key == 2 or key == 4):
#          # adding both 2nd and 3rd sessions:
#          for c in clients_to_add:
#              for f in session.query(File).filter(File.client_id == c).filter(or_(File.session == 2, File.session == 3)):
#                  if verbose > 1: 
#                      print("    Adding to the protocol Client's {} file {}...".format(f.client_id, f.path))
#                  prot_purp.files.append(f)

  session.commit()
#  if verbose > 1:
#      print("\n\n")
#      print("--- Summary of clients added to groups /purposes ---")
#      print("   [displayed Client.id's]")
#      print("Persons:")
#      print("One session       = {}".format(one_pers_list))
#      print("Multiple sessions = {}".format(mult_pers_list))
#      print("---------------------------------------------")
#      print("Persons with only 1 session are added to the 'world' data set \n(devided between 'large' and 'small' protocol):")
#      print("Protocol 'small' --- {}".format(one_pers_list[0:small_one_pers_count]))
#      print("Protocol 'large' --- {}".format(one_pers_list[small_one_pers_count:]))
#      print("---------------------------------------------")
#      print("Persons with multiple sessions are devided in 2 parts for different \npurposes:")
#      print("For world / dev data set -- {}".format(world_dev_pers_list))
#      print("For eval data set -- {}".format(eval_pers_list))
#      print("---------------------------------------------")
#      print("Multiple person  world / dev set is devided for protocols 'small' \nand 'large':")
#      print("World/dev -- small -- {}".format(world_dev_pers_list[0:small_mult_pers_count]))
#      print("World/dev -- large -- {}".format(world_dev_pers_list[small_mult_pers_count:]))
#      print("---------------------------------------------")
#      print("In summary -- persons for each protocol / group:")
#      print("---------------------------------------------")
#      print("protocol          SMALL:")
#      print("World -- {}".format((one_pers_list[0:small_one_pers_count] + world_dev_pers_list[0:small_mult_pers_count])))
#      print("Dev   -- empty")
#      print("Eval  -- empty")
#      print("---------------------------------------------")
#      print("protocol          LARGE:")
#      print("World -- {}".format((one_pers_list[small_one_pers_count:] + world_dev_pers_list[small_mult_pers_count:])))
#      print("Dev   -- {}".format(world_dev_pers_list[small_mult_pers_count:]))
#      print("Eval  -- {}".format(eval_pers_list))
#      print("\n\n")
#      print("As enroll data are used session Nr - 1 data")
#      print("As probe data are used session Nr - 2 and 3 data")
#      print("")      
#      print("Now we can count for files in each  protocol:")
#      print("---------------------------------------------")
#      print("protocol          SMALL:")
#      x = session.query(File).filter(File.client_id.in_(one_pers_list[0:small_one_pers_count] + world_dev_pers_list[0:small_mult_pers_count])).all()
#      print("World -- {}, enroll -- 0, probe -- 0".format(len(x)))
#      print("Dev: train -- 0, enroll -- 0, probe -- 0")
#      print("Eval: train -- 0, enroll -- 0, probe -- 0")
#      print("---------------------------------------------")
#      print("protocol          LARGE:")
#      print("World: train -- {}, enroll -- 0, probe -- 0".format(session.query(File).filter(File.client_id.in_(one_pers_list[small_one_pers_count:] + world_dev_pers_list[small_mult_pers_count:])).count()))
#      print("Dev: train -- 0, enroll -- {}, probe -- {}".format(session.query(File).filter(File.client_id.in_(world_dev_pers_list[small_mult_pers_count:])).filter(File.session.in_(["1"])).count(),\
#      session.query(File).filter(File.client_id.in_(world_dev_pers_list[small_mult_pers_count:])).filter(File.session.in_(["2", "3"])).count()))
#      print("Eval: train -- 0, enroll -- {}, probe -- {}".format(session.query(File).filter(File.client_id.in_(eval_pers_list)).filter(File.session.in_(["1"])).count(),\
#      session.query(File).filter(File.client_id.in_(eval_pers_list)).filter(File.session.in_(["2","3"])).count()))
#      print("---------------------------------------------")
#      print("---------------------------------------------")


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
