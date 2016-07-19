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

"""
This module provides the Dataset interface allowing the user to query the
BIOWAVE database in the most obvious ways.
"""

import os
import six
from bob.db.base import utils
from .models import *
from .driver import Interface

import bob.db.base

SQLITE_FILE = Interface().files()[0]

class Database(bob.db.base.SQLiteDatabase):
  """
  The dataset class opens and maintains a connection opened to the Database.

  It provides many different ways to probe for the characteristics of the data
  and for the data itself inside the database.
  """

  def __init__(self, original_directory = None, original_extension = '.png'):
    # call base class constructor
    bob.db.base.SQLiteDatabase.__init__(self, SQLITE_FILE, File)
    
  #############################################################################
  ## help methods: ############################################################
  #############################################################################
  def groups(self):
    """Returns the names of all registered groups"""
    return ProtocolPurpose.group_choices

    #  def client_genders(self):
    #      """Returns the names of all gender choices in the database"""
    #      return Client.gender_choices
  
  def client_hands(self):
      """Returns the names of all hand choices"""
      return Client.hand_choices

  def protocol_names(self):
    """Returns all registered protocol names"""

    l = self.protocols()
    retval = [str(k.name) for k in l]
    return retval

  def protocols(self):
    """Returns all registered protocols"""

    return list(self.query(Protocol))

  def has_protocol(self, name):
    """Tells if a certain protocol is available"""

    return self.query(Protocol).filter(Protocol.name==name).count() != 0

  def protocol(self, name):
    """Returns the protocol object in the database given a certain name. Raises
    an error if that does not exist."""

    return self.query(Protocol).filter(Protocol.name==name).one()

  def protocol_purposes(self):
    """Returns all registered protocol purposes"""

    return list(self.query(ProtocolPurpose))


  def purposes(self):
    """Returns the list of allowed purposes"""

    return ProtocolPurpose.purpose_choices

#  def file_sessions(self):
#    """Returns the list of alloved session numbers"""
#
#    return File.session_choices
#
#  def file_attempts(self):
#    """Returns the list of alloved attempt numbers"""
#
#    return File.attempt_choices
#
#  def file_im_numbers(self):
#    """Returns the list of alloved image numbers (in an ettempt)"""
#
#    return File.image_no_choices
      
  #############################################################################
  ## end of help methods ######################################################
  #############################################################################

  def clients(self, hands = None):
    """Returns a list of :py:class:`.Client` for the specific query by the user.
       Clients correspond to the BIOWAVE database CLIENT entries -- each entry 
       represents a person's hand.

    Keyword Parameters:

   
    hands
        client's hand -- L (left), R (right) -- each database's client entry is 
        a person's one hand -- in this way databases entry count is doubled.    
    
    Returns: A list containing all the clients which have the given hand choise.
    """

    #genders = self.check_parameters_for_validity(genders, "gender", self.client_genders())
    hands = self.check_parameters_for_validity(hands, "hand", self.client_hands())
    
    # List of the clients
    q = self.query(Client)
#    if genders:
#      q = q.filter(Client.gender.in_(genders))
    if hands:
      q = q.filter(Client.hand.in_(hands))   
    q = q.order_by(Client.id)
    return list(q)
    
  def models(self, hands = None):
    """Returns a list of :py:class:`.Client` for the specific query by the user.
       Models correspond to Clients for the BIOWAVE TEST database.

    Keyword Parameters:
    
    
    hands
        client's hand -- L (left), R (right) -- each database's client entry is 
        a person's one hand -- in this way databases entry count is doubled.    
    
    Returns: A list containing all the clients which have the given hand choise.
    """

    return self.clients(hands)
    
  def model_ids(self, hands = None):
    """Returns a list of model ids for the specific query by the user.
       Models correspond to the BIOWAVE database CLIENT entries -- each entry 
       represents a person's hand.

    Keyword Parameters:
    
    hands
        client's hand -- L (left), R (right) -- each database's client entry is 
        a person's one hand -- in this way databases entries are doubled.    
    
    Returns: A list containing all the client ids having the given hand choises.
    """
      
    return [client.id for client in self.clients(hands)]

  def has_client_id(self, id):
    """Returns True if in the BIOWAVE database is a client with a certain integer 
       identifier.
    """

    return self.query(Client).filter(Client.id==id).count() != 0

  def client(self, id):
    """Returns the client object in the database given a certain id. Raises
    an error if that does not exist."""

    return self.query(Client).filter(Client.id==id).one()

  def objects(self, protocol=None, groups=None, purposes=None, model_ids=None):
    """Returns a list of :py:class:`.File` for the specific query by the user.

    Keyword Parameters:

    protocol
      BIOWAVE_TEST database has only 1 protocol -- 'all'.

    groups
      One of the groups ('dev', 'eval') or a tuple with several of them.
      If 'None' is given (this is the default), it is considered the same as a
      tuple with all possible values.

    purposes
      The purposes required to be retrieved ('enroll', 'probe') or a tuple
      with several of them. If 'None' is given (this is the default), it is
      considered the same as a tuple with all possible values. 
      Please be aware, that purpose "train" is only for group "world" and it is
      the only one purpose for this group.

    model_ids
      Only retrieves the files for the provided list of model ids (claimed
      BIOWAVE database client id). The model ids are string.  If 'None' is given (this is
      the default), no filter over the model_ids is performed.
    
    Returns: A list of :py:class:`.File` objects.
    """


    protocol = self.check_parameters_for_validity(protocol, "protocol", self.protocol_names())
    purposes = self.check_parameters_for_validity(purposes, "purpose", self.purposes())
    groups = self.check_parameters_for_validity(groups, "group", self.groups())
    # special BIOWAVE database file features:
#    sessions = self.check_parameters_for_validity(sessions, "session", self.file_sessions()) 
#    attempts = self.check_parameters_for_validity(attempts, "attempt", self.file_attempts()) 
#    im_numbers = self.check_parameters_for_validity(im_numbers, "attempt", self.file_im_numbers()) 


    import collections
    if(model_ids is None):
      model_ids = ()
    elif(not isinstance(model_ids,collections.Iterable)):
      model_ids = (model_ids,)

    # Now query the database
    retval = []

    for k in groups:
        q = self.query(File).join((ProtocolPurpose, File.protocolPurposes)).join(Protocol).\
            filter(Protocol.name.in_(protocol)).filter(ProtocolPurpose.sgroup == k).\
            filter(ProtocolPurpose.purpose.in_(purposes))
        if model_ids:
          q = q.filter(File.client_id.in_(model_ids))
        q = q.order_by(File.client_id)
        retval += list(q)    
        
        
    return list(set(retval)) # To remove duplicates

#  def annotation(self, file):
#    """Returns the annotation for the given BIOWAVE database file object.
#
#    Keyword Parameters:
#
#    file
#      The ``File`` object to retrieve the annotations for.
#
#    Returns: the ``Annotations`` object for the given ``file`` object, if 
#    such object exists.
#    """
#
#    self.assert_validity()
#    # return the annotations as returned by the call function of the Annotation object
#    return file.annotation
#
#  def annotations_path(self, file):
#    """Returns the annotation's path for a given for the given BIOWAVE database 
#       file object. If there is no anotation, ``None`` is returned
#       
#    Keyword Parameters:
#
#    file
#      The ``File`` object to retrieve the annotations for.
#
#    Returns: the path as string object for the given ``file`` annotation, if there
#    exist one. Else ``None`` is returned.
#    """
#
#    self.assert_validity()
#    if file.annotation != None:
#        return str(file.annotation.path)
#    else:
#        return None
