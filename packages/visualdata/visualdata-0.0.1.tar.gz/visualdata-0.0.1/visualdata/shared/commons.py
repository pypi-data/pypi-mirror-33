"""Shared definition for constants, classes.
"""


class DataType(object):
  """Type of the data.

  Used to categorize data.
  """
  TRAIN = 0
  VALIDATE = 1
  TEST = 2
  LABEL = 3


class DataFileType(object):
  """Type of data file.
  """
  METADATA = 0
  TFRECORD = 1
  HDF5 = 2


class InputDataFormat(object):
  """Format of input data.
  """
  FILE_NAME = 0
  IMG_DATA = 1
