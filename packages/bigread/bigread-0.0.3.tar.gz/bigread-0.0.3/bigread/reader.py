from six import string_types
from collections import deque
import codecs
import os

types = {
  'file': string_types,
  'encoding': string_types,
  'block_size': int,
}

class Reader:
  def __init__(self, *args, **kwargs):
    self.file = kwargs.get('file', None) # path to infile
    self.encoding = kwargs.get('encoding', 'utf8') # file encoding
    self.block_size = kwargs.get('block_size', 100000) # bytes to read per block
    self.position = 0 # last read byte from file
    self.line_num = 0 # last read line number
    self.number_lines = False # return tuples of (number, line)?
    self.lines = deque() # queue of lines
    self.end = os.path.getsize(self.file) # size of infile in bytes
    self.validate_args(kwargs)

  def __getitem__(self, x):
    '''Add support for self[attr] lookups'''
    return getattr(self, x)

  def __setitem__(self, attr, x):
    '''Add support for attribute assignments after construction'''
    setattr(self, attr, x)

  def __iter__(self):
    '''Add an iteration method for streaming lines'''
    while self.position < self.end or self.lines:
      if len(self.lines) == 0:
        self.read()
      yield self.pop_line()

  def read(self):
    '''Read additional lines from the file'''
    with open(self.file) as f:
      f.seek(self.position + self.block_size) # read a block of text
      f.readline() # advance to the next newline character
      end = f.tell() # find the resulting position
      f.seek(self.position) # rewind to the starting position
      lines = f.read(end - self.position).splitlines() # get all lines in block
      numbered = [(self.line_num + idx, i) for idx, i in enumerate(lines)]
      self.lines.extend(numbered) # add numbered lines to class line store
      self.position = end # store the resulting position
      self.line_num += len(numbered)

  def next(self):
    '''Return the nth line from the text'''
    if (self.position >= self.end) and (not self.lines):
      return None
    elif len(self.lines) == 0:
      self.read()
    self.line_num += 1
    return self.pop_line()

  def pop_line(self):
    '''Return the left-most line in the line queue'''
    if self.number_lines:
      return self.lines.popleft()
    return self.lines.popleft()[1]

  def validate_args(self, kwargs):
    '''
    Validate that the user passed valid aruments
    @args:
      {dict} kwargs: all user-provided kwargs
    '''
    for i in kwargs: # typecheck inputs
      if i not in dir(self):
        continue
      t = types[i]
      if not isinstance(self[i], t):
        i_type = t.__name__ if t not in [string_types] else t[0].__name__
        raise TypeError('`' + i + '` argument should be a ' + i_type)