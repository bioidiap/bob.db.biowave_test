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

"""A few checks for the BIOWAVE database.
"""

import os
import bob.db.biowave_test


def db_available(test):
  """Decorator for detecting if OpenCV/Python bindings are available"""
  from bob.io.base.test_utils import datafile
  from nose.plugins.skip import SkipTest
  import functools

  @functools.wraps(test)
  def wrapper(*args, **kwargs):
    dbfile = datafile("db.sql3", __name__, None)
    if os.path.exists(dbfile):
      return test(*args, **kwargs)
    else:
      raise SkipTest("The database file '%s' is not available; did you forget to run 'bob_dbmanage.py %s create' ?" % (dbfile, 'biowave_test'))

  return wrapper


@db_available
def test_clients():
  db = bob.db.biowave_test.Database()
  
  assert len(db.groups()) == 2
  assert len(db.client_hands()) == 2
  assert len(db.protocol_names()) == 1
  assert len(db.protocols()) == 1
  assert db.has_protocol('all')
  assert len(db.protocol_purposes()) == 4
  assert len(db.purposes()) == 2  
    
  assert len(db.clients()) == 40
  assert len(db.clients(hands = ["R", "L"])) == 40
  assert len(db.clients(hands = "L")) == 20
  assert len(db.clients(hands = "R"))   == 20
  assert len(db.clients(hands = "L", protocol = 'all'))   == 20
  assert len(db.clients(hands = "R", protocol = 'all'))   == 20
  assert len(db.clients(hands = "R", protocol = 'all', groups = 'dev')) == 0
  assert len(db.clients(hands = "R", protocol = 'all', groups = 'eval')) == 20
  assert len(db.clients(hands = "L", protocol = 'all', groups = 'dev')) == 20
  assert len(db.clients(hands = "L", protocol = 'all', groups = 'eval')) == 0
  
  #assert len(db.models()) == 40
  #assert len(db.models(hands = ["R", "L"])) == 40
  #assert len(db.models(hands = "L")) == 20
  #assert len(db.models(hands = "R"))   == 20
  #assert len(db.models(groups='dev'))   == 20
  #assert len(db.models(groups='eval'))   == 20
  
@db_available
def test_objects():
  db = bob.db.biowave_test.Database()
  # protocol ALL:  
  
  assert len(db.objects()) == 200
  assert len(db.objects(protocol = 'all')) == 200

  assert len(db.objects(protocol = 'all', groups = 'dev')) == 100
  assert len(db.objects(protocol = 'all', groups = 'eval')) == 100

  assert len(db.objects(groups = 'dev')) == 100
  assert len(db.objects(groups = 'eval')) == 100

  assert len(db.objects(protocol = 'all', purposes = 'enroll')) == 80
  assert len(db.objects(protocol = 'all', purposes = 'probe')) == 120

  assert len(db.objects(purposes = 'enroll')) == 80
  assert len(db.objects(purposes = 'probe')) == 120

  assert len(db.objects(protocol = 'all', groups = 'dev', purposes = 'enroll')) == 40
  assert len(db.objects(protocol = 'all', groups = 'dev', purposes = 'probe'))  == 60

  assert len(db.objects(protocol = 'all', groups = 'eval', purposes = 'enroll')) == 40
  assert len(db.objects(protocol = 'all', groups = 'eval', purposes = 'probe')) == 60

  assert len(db.objects(groups = 'dev', purposes = 'enroll')) == 40
  assert len(db.objects(groups = 'dev', purposes = 'probe'))  == 60

  assert len(db.objects(groups = 'eval', purposes = 'enroll')) == 40
  assert len(db.objects(groups = 'eval', purposes = 'probe')) == 60

  assert len(db.objects(protocol = 'all', model_ids = ["c_1_i_1"])) == 1
  assert len(db.objects(protocol = 'all', model_ids = ["c_1_i_1"], purposes = 'enroll')) == 1
  assert len(db.objects(protocol = 'all', model_ids = ["c_1_i_1"], purposes = 'probe')) == 120

  #test is removed, because now valuse is checked with model_ids values in the current group
  #assert len(db.objects(protocol = 'all', model_ids = ["c_1_i_1"], groups = 'eval')) == 0
  assert len(db.objects(protocol = 'all', model_ids = ["c_1_i_1"], groups = 'dev')) == 1

  assert len(db.objects(protocol = 'all', model_ids = ["c_1_i_1"], groups = 'dev', purposes = 'enroll')) == 1
  assert len(db.objects(protocol = 'all', model_ids = ["c_1_i_1"], groups = 'dev', purposes = 'probe')) == 60

  assert len(db.objects(model_ids = ["c_1_i_1"])) == 1
  assert len(db.objects(model_ids = ["c_1_i_1"], purposes = 'enroll')) == 1
  assert len(db.objects(model_ids = ["c_1_i_1"], purposes = 'probe')) == 120

  #test is removed, because now valuse is checked with model_ids values in the current group  
  #assert len(db.objects(model_ids = ["c_1_i_1"], groups = 'eval')) == 0
  assert len(db.objects(model_ids = ["c_1_i_1"], groups = 'dev')) == 1

  assert len(db.objects(model_ids = ["c_1_i_1"], groups = 'dev', purposes = 'enroll')) == 1
  assert len(db.objects(model_ids = ["c_1_i_1"], groups = 'dev', purposes = 'probe')) == 60

  assert len(db.objects(protocol = 'all', model_ids = ["c_2_i_2"], groups = 'eval')) == 1
  #test is removed, because now valuse is checked with model_ids values in the current group
  #assert len(db.objects(protocol = 'all', model_ids = ["c_1_i_1"], groups = 'dev')) == 0
  assert len(db.objects(protocol = 'all', model_ids = ["c_2_i_2"], groups = 'eval', purposes = 'enroll')) == 1
  assert len(db.objects(protocol = 'all', model_ids = ["c_2_i_2"], groups = 'eval', purposes = 'probe')) == 60

  assert len(db.objects(model_ids = ["c_1_i_1","c_2_i_1","c_3_i_1","c_4_i_1","c_5_i_1"])) == 5
  assert len(db.objects(model_ids = ["c_6_i_1","c_7_i_1","c_8_i_1","c_9_i_1","c_10_i_1"])) == 5
  assert len(db.objects(model_ids = ["c_11_i_1","c_12_i_1","c_13_i_1","c_14_i_1","c_15_i_1"])) == 5
  
  assert db.objects(model_ids = ["c_1_i_1"])[0].unique_file_name == 1
  assert db.objects(model_ids = ["c_1_i_2"])[0].unique_file_name == 1
  assert db.objects(model_ids = ["c_40_i_1"])[0].unique_file_name == 40
  assert db.objects(model_ids = ["c_40_i_2"])[0].unique_file_name == 40
  
  temp1 = db.objects(model_ids = ["c_7_i_1"], groups = 'dev', purposes='probe')
  temp1_ids = []
  for m in temp1:
    temp1_ids.append(m.unique_file_name)
  temp1_ids = list(set(temp1_ids))
  temp1_ids.sort()
  
  temp2 = db.clients(protocol = 'all', groups = 'dev')
  temp2_ids = []
  for m in temp2:
    temp2_ids.append(m.id)
  temp2_ids = list(set(temp2_ids))
  temp2_ids.sort()
  assert temp1_ids == temp2_ids
  
  
  temp1 = db.objects(model_ids = ["c_38_i_2"], groups = 'eval', purposes='probe')
  temp1_ids = []
  for m in temp1:
    temp1_ids.append(m.unique_file_name)
  temp1_ids = list(set(temp1_ids))
  temp1_ids.sort()
  temp2 = db.clients(protocol = 'all', groups = 'eval')
  temp2_ids = []
  for m in temp2:
    temp2_ids.append(m.id)
  temp2.sort()
  assert temp1_ids == temp2_ids



@db_available
def test_driver_api():
  from bob.db.base.script.dbmanage import main
  assert main('biowave_test dumplist --self-test'.split()) == 0
  assert main('biowave_test dumplist --protocol=all --group=dev --purpose=enroll --self-test'.split()) == 0
  assert main('biowave_test dumplist --protocol=all --group=dev --purpose=enroll --models=c_7_i_1 --self-test'.split()) == 0
  assert main('biowave_test checkfiles --self-test'.split()) == 0
  assert main('biowave_test reverse Person_01/Left/BioPic_20160425_114336 --self-test'.split()) == 0
  assert main('biowave_test path 2 --self-test'.split()) == 0
  assert main('biowave_test download --force'.split()) == 0


