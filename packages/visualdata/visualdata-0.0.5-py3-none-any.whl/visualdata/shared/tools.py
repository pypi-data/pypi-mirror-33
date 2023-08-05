"""Shared tool functions.
"""
"""Shared tool functions.
"""

import json
import os
import glob

from visualdata.shared import commons


def pretty_print_json(obj_val):
  """Print a formatted json object.
  """
  print(json.dumps(obj_val, indent=2, sort_keys=True))


def gen_data_filename(fn_prefix,
                      file_type=commons.DataFileType.METADATA,
                      data_type=commons.DataType.TRAIN):
  """Generate filename for corresponding data.

  Args:
    fn_prefix: prefix of the filename.
    file_type: target file type.
    data_type: type of data file.
  Returns:
    generated filename.
  """
  if file_type == commons.DataFileType.METADATA:
    if data_type == commons.DataType.TRAIN:
      return "{}__train.csv".format(fn_prefix)
    if data_type == commons.DataType.TEST:
      return "{}__test.csv".format(fn_prefix)
    if data_type == commons.DataType.LABEL:
      return "{}__labels.txt".format(fn_prefix)
  if file_type == commons.DataFileType.TFRECORD:
    if data_type == commons.DataType.TRAIN:
      return "{}__train.tfrecord".format(fn_prefix)
    if data_type == commons.DataType.TEST:
      return "{}__test.tfrecord".format(fn_prefix)
    if data_type == commons.DataType.VALIDATE:
      return "{}__validate.tfrecord".format(fn_prefix)
  if file_type == commons.DataFileType.HDF5:
    if data_type == commons.DataType.TRAIN:
      return "{}__train.h5".format(fn_prefix)
    if data_type == commons.DataType.TEST:
      return "{}__test.h5".format(fn_prefix)
    if data_type == commons.DataType.VALIDATE:
      return "{}__validate.h5".format(fn_prefix)


def convert_data_filename(input_fn, dst_file_type, dst_data_type):
  """Convert one data filename to another.

  Args:
    input_fn: input data filename.
    There should be no '__' in filename other than the last part.
    dst_file_type: target data file type.
    dst_data_type: target data type.
  Returns:
    converted data filename.
  """
  sep_idx = input_fn.find("__")
  assert sep_idx != -1, "invalid input data filename."
  return gen_data_filename(input_fn[:sep_idx], dst_file_type, dst_data_type)


def verify_fn_ext(fn, ext):
  """Assert if file is in valid format.

  Args:
    fn: filename.
    ext: file extension, e.g. jpg, png.
  """
  assert os.path.splitext(fn)[1] == ext, "file must be in {} format.".format(
      ext)


def list_files(target_dir, fn_exts):
  """List all files match given extensions.

  Match both upper and lower cases.

  Args:
    fn_exts: a list of file extension in the form of "*.jpg".

  Returns:
    a list of found files.
  """
  all_exts = []
  for ext in fn_exts:
    all_exts.append(ext.lower())
    all_exts.append(ext.upper())
  all_exts = set(all_exts)
  all_fns = []
  for cur_ext in all_exts:
    cur_fns = glob.glob(os.path.join(target_dir, cur_ext))
    all_fns.extend(cur_fns)
  return all_fns
