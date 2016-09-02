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
Table models and functionality for the BIOWAVE test database - the small `test`
database with only 20 person's data
"""


import bob.db.base.utils
from sqlalchemy import Table, Column, Integer, String, ForeignKey, or_, and_
from bob.db.base.sqlalchemy_migration import Enum, relationship
from sqlalchemy.orm import backref
from sqlalchemy.ext.declarative import declarative_base

import bob.db.base
import bob.db.base.file
import os.path

Base = declarative_base()

protocolPurpose_file_association = Table('protocolPurpose_file_association', Base.metadata,
  Column('protocolPurpose_id', Integer, ForeignKey('protocolPurpose.id')),
  Column('file_id',  Integer, ForeignKey('file.id')))

class Client(Base):
  """Database clients, marked by an integer identifier.
     Each client entry represents a single humans hand, in this way database 
     entries are doubled.
  """

  __tablename__ = 'client'

  # Key identifier for the client
  id = Column(Integer, primary_key=True)
  original_client_id = Column(Integer) 
  
  # Other Client atributes:
  #gender_choices = ('M', 'F')
  #gender         = Column(Enum(*gender_choices))
  hand_choices   = ('L', 'R')
  hand           = Column(Enum(*hand_choices))
  
  def __init__(self, original_client_id, hand): # gender, 
    """
    Client constructor
    """
    self.original_client_id     = original_client_id
    #self.gender                 = gender
    self.hand                   = hand

  def __repr__(self):
    return "Client(assigned SQL id = {}, original client id = {}, hand = {})".format(self.id, self.original_client_id, self.hand)


class File(Base, bob.db.base.File):
  """Generic file container"""   
  __tablename__ = 'file'
  # Key identifier for the file
  id = Column(Integer, primary_key=True)
  # Key identifier of the client associated with this file
  client_id = Column(Integer, ForeignKey('client.id')) # for SQL
  # Unique path to this file inside the database
  path = Column(String(100), unique=True)
  # extra identificators:
#  session_choices = ("1","2","3")
#  session = Column(Enum(*session_choices))
#  attempt_choices = ("1","2","3", "4", "5")
#  attempt = Column(Enum(*attempt_choices))
#  image_no_choices = ("1","2","3", "4", "5")
#  image_no = Column(Enum(*image_no_choices))
  
  # For Python: A direct link to the client object that this file belongs to:
  client = relationship("Client", backref=backref("files", order_by=id))
  # For Python: A direct link to the annotation object that file belongs to this file:
  #annotation = relationship("Annotation", backref=backref("file", order_by=id, uselist=False), uselist=False)
  
  # this column is not really required as it can be computed from other
  # information already in the database, it is only an optimisation to allow us
  # to quickly filter files by ``model_id``
  model_id = Column(String(9), unique=True)
  

  def __init__(self, client_id, path, nr): # , f_session, f_attempt, f_image_no
    # call base class constructor, client ID - SQL table ID;
    # path - A relative path, which includes file name but excludes file extension
    # Because this is an SQL database, you SHOULD NOT assign the file_id
    bob.db.base.File.__init__(self, path = path)
    self.client_id = client_id
    self.model_id = "c_{}_i_{}".format(client_id,nr)
#    self.session = f_session
#    self.attempt = f_attempt
#    self.image_no = f_image_no
  
  def __repr__(self):
    return "\nFile(assigned SQL id = {}, Client id = {}, path = {})"\
    .format(self.id, self.client_id, self.path)
  
  @property
  def unique_file_name(self):
    """Unique name for a given file (image) in the database"""

    return self.client_id

  
#class Annotation(Base):
#  """
#  Annotations of the BIOWAVE database.
#  Anotations need to be saved at location specified using comand line interface (parser).
#  If the original database file is named e.g.:
#  
#  004_M_R_S01_A04_1
#  
#  than the annotation file name:
#  
#  004_M_R_S01_A04_1_annotation
#  """
#  __tablename__ = 'annotation'
#
#  id = Column(Integer, primary_key=True)
#  # file ID to which the anotation belongs:  
#  file_id = Column(Integer, ForeignKey('file.id'))
#  #Anotation's path:
#  path = Column(String(100), unique=True)
#
#  # all the job to corectly assign file with anotation has to be done
#  # at the "create" layer
#  def __init__(self, file_id, path):
#      self.file_id = file_id
#      self.path = path
#  def __repr__(self):
#      return "Annotation('assigned SQL id = {}, File id = {}, path = {})"\
#      .format(self.id, self.file_id, self.path)


class Protocol(Base):
  """BIOWAVE protocols"""

  __tablename__ = 'protocol'
  # Unique identifier for this protocol object
  id = Column(Integer, primary_key=True)
  # Name of the protocol associated with this object
  name = Column(String(20), unique=True)

  def __init__(self, name):
    self.name = name

  def __repr__(self):
    return "Protocol name - {}".format(self.name)
  #   return self.name

class ProtocolPurpose(Base):
  """BIOWAVE protocol purposes"""

  __tablename__ = 'protocolPurpose'
  # Unique identifier for this protocol purpose object
  id = Column(Integer, primary_key=True)
  # Id of the protocol associated with this protocol purpose object
  protocol_id = Column(Integer, ForeignKey('protocol.id')) # for SQL
  # Group associated with this protocol purpose object
  group_choices = ('dev', 'eval')
  sgroup = Column(Enum(*group_choices))
  # Purpose associated with this protocol purpose object
  purpose_choices = ('enroll', 'probe')
  purpose = Column(Enum(*purpose_choices))

  # For Python: A direct link to the Protocol object that this ProtocolPurpose belongs to
  protocol = relationship("Protocol", backref=backref("purposes", order_by=id))
  # For Python: A link to the File objects associated with this ProtcolPurpose
  files = relationship("File", secondary=protocolPurpose_file_association, backref=backref("protocolPurposes", order_by=id))

  def __init__(self, protocol_id, sgroup, purpose):
    self.protocol_id = protocol_id
    self.sgroup = sgroup
    self.purpose = purpose

  def __repr__(self):
    return "ProtocolPurpose('%s', '%s', '%s')" % (self.protocol.name, self.sgroup, self.purpose)

