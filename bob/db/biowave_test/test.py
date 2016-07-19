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
      raise SkipTest("The database file '%s' is not available; did you forget to run 'bob_dbmanage.py %s create' ?" % (dbfile, 'biowave'))

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
  
  assert len(db.models()) == 40
  assert len(db.models(hands = ["R", "L"])) == 40
  assert len(db.models(hands = "L")) == 20
  assert len(db.models(hands = "R"))   == 20
  
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

  assert len(db.objects(protocol = 'all', model_ids = [1])) == 5
  assert len(db.objects(protocol = 'all', model_ids = [1], purposes = 'enroll')) == 2
  assert len(db.objects(protocol = 'all', model_ids = [1], purposes = 'probe')) == 3

  assert len(db.objects(protocol = 'all', model_ids = [1], groups = 'eval')) == 0
  assert len(db.objects(protocol = 'all', model_ids = [1], groups = 'dev')) == 5

  assert len(db.objects(protocol = 'all', model_ids = [1], groups = 'dev', purposes = 'enroll')) == 2
  assert len(db.objects(protocol = 'all', model_ids = [1], groups = 'dev', purposes = 'probe')) == 3

  assert len(db.objects(model_ids = [1])) == 5
  assert len(db.objects(model_ids = [1], purposes = 'enroll')) == 2
  assert len(db.objects(model_ids = [1], purposes = 'probe')) == 3

  assert len(db.objects(model_ids = [1], groups = 'eval')) == 0
  assert len(db.objects(model_ids = [1], groups = 'dev')) == 5

  assert len(db.objects(model_ids = [1], groups = 'dev', purposes = 'enroll')) == 2
  assert len(db.objects(model_ids = [1], groups = 'dev', purposes = 'probe')) == 3

  assert len(db.objects(protocol = 'all', model_ids = [2], groups = 'eval')) == 5
  assert len(db.objects(protocol = 'all', model_ids = [2], groups = 'dev')) == 0
  assert len(db.objects(protocol = 'all', model_ids = [2], groups = 'eval', purposes = 'enroll')) == 2
  assert len(db.objects(protocol = 'all', model_ids = [2], groups = 'eval', purposes = 'probe')) == 3

  assert len(db.objects(model_ids = [1,2,3,4,5])) == 25
  assert len(db.objects(model_ids = [6,7,8,9,10])) == 25
  assert len(db.objects(model_ids = [11,12,13,14,15])) == 25
  assert len(db.objects(model_ids = [16,17,18,19,20])) == 25

  assert len(db.objects(protocol = 'all', model_ids = [1,2,3,4,5])) == 25
  assert len(db.objects(protocol = 'all', model_ids = [6,7,8,9,10])) == 25
  assert len(db.objects(protocol = 'all', model_ids = [11,12,13,14,15])) == 25
  assert len(db.objects(protocol = 'all', model_ids = [16,17,18,19,20])) == 25


@db_available
def test_driver_api():
  None
  from bob.db.base.script.dbmanage import main
  assert main('biowave_test dumplist --self-test'.split()) == 0
  assert main('biowave_test dumplist --protocol=all --group=dev --purpose=enroll --client=1 --self-test'.split()) == 0
  assert main('biowave_test checkfiles --self-test'.split()) == 0
  assert main('biowave_test reverse Person_01/Left/BioPic_20160425_11433 --self-test'.split()) == 0
  assert main('biowave_test path 2 --self-test'.split()) == 0
