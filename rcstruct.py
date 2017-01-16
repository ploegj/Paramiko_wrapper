#! /usr/bin/python

class rcstruct:

#  def __init__(self, rc=0, callrc=0, errstr = 'OK', data = None):
  def __init__(self):
    #self.rc     = rc
    #self.callrc = callrc
    #self.errstr = errstr
    #self.data   = data
    self.rc     = 0
    self.callrc = 0
    self.errstr = 'OK'
    self.data   = None

  def set_rc(self, rc=0):
    self.rc = rc

  def set_callrc(self, rc=0):
    self.callrc = rc

  def set_errstr(self, errstr='OK'):
    self.errstr = errstr

  def set_data(self, data=None):
    self.data = data

  def get_rc(self):
    return(self.rc)

  def get_callrc(self):
    return(self.callrc)

  def get_errstr(self):
    return(self.errstr)

  def get_data(self):
    return(self.data)
