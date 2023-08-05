"""Class interface for image classification dataset.

A dataset is usually made of three parts.
1) datainfo: general info about the dataset, saved in json.
2) metadata: a generic format for listing dataset entries in csv.
3) data file: binary data files on disk to store actual data.
"""

import abc
import csv
import json
import math
import os
import random

from visualdata.shared import commons, tools
from visualdata.shared.dataset import DatasetInfoKeyBase, DataSetInfoBase, DatasetBase


class DatasetInfoKey(DatasetInfoKeyBase):
  """Data info key name.
  """
  IMG_FORMAT = "img_format"
  MULTI_LABEL = "multi_label"


class DataSetInfo(DataSetInfoBase):
  """Info class for image classification dataset.
  """

  def __init__(self, save_dir, multi_label=False):
    assert save_dir is not None, "save directory cannot be empty"
    self.save_dir = save_dir
    info_fn = os.path.join(save_dir, "info.json")
    super(DataSetInfo, self).__init__(info_fn)
    if os.path.exists(info_fn):
      # load existing info.
      self.load_info()
    else:
      # init custom keys.
      self._ds_info[DatasetInfoKey.NAME] = "dataset"
      self._ds_info[DatasetInfoKey.MULTI_LABEL] = multi_label

  def get_value(self, key_name):
    # label key.
    if key_name in [
        DatasetInfoKey.LABEL_ID_TO_NAME, DatasetInfoKey.LABEL_NAME_TO_ID
    ]:
      return self._ds_info[DatasetInfoKey.LABELS][key_name]
    else:
      return super(DataSetInfo, self).get_value(key_name)

  def set_value(self, key_name, val):
    if key_name in [
        DatasetInfoKey.LABEL_ID_TO_NAME, DatasetInfoKey.LABEL_NAME_TO_ID
    ]:
      self._ds_info[DatasetInfoKey.LABELS][key_name] = val
    else:
      super(DataSetInfo, self).set_value(key_name, val)


class Dataset(DatasetBase):
  """Image classification dataset.

  Each image can have one or more labels.

  Metadata file format:
  The first row (header) describes the meaning of each column.
  Each row contains: image file path or url, value for each label type in following columns.
  """
  __metadata__ = abc.ABCMeta

  ds_info = None

  def __init__(self, save_dir, ds_info_=None):
    """Initialization.

    Args:
      ds_name: dataset name.
      save_dir: directory to save dataset related data.
      Good for intermediate data.
    """
    if ds_info_ is None:
      self.ds_info = DataSetInfo(save_dir)
    else:
      self.ds_info = ds_info_

  """ Dataset labels and metadata. """

  def get_label_name(self, label_id):
    """Map id to name.
    """
    return self.ds_info.get_label_name(label_id)

  def get_label_id(self, label_name):
    """Map name to id.
    """
    return self.ds_info.get_label_id(label_name)

  def is_multi_label(self):
    """Check if the dataset supports multi labels.
    """
    return self.ds_info.get_value(DatasetInfoKey.MULTI_LABEL)

  """ Build dataset. """

  def gen_metadata_from_folder(self, img_dir, train_ratio=0.8):
    """Generate csv files for training and testing data.

    The images are organized by categories in separate folder.
    Three csv files will be generated: train metadata, test metadata
    and label names.
    Each metadata file has format: <img_path, img_label>.

    Args:
      img_dir: root directory. Each subfolder is a category.
      save_fn_prefix: prefix for saved files. train and test.
      files will have corresponding suffix appended.
      train_ratio: ratio between train and test data.

    Returns:
      train meta fn, test meta fn, label id to name mapper, label name to id mapper.
    """
    # multi label is not supported now.
    assert not self.is_multi_label()
    # list all category directories.
    cat_dirs = os.listdir(img_dir)
    cat_dirs = [os.path.join(img_dir, x) for x in cat_dirs]
    cat_dirs = [x for x in cat_dirs if os.path.isdir(x)]
    img_exts = ["*.png", "*.jpg", "*.bmp", "*.jpeg"]
    all_data = [("img_fn", "category")]

    # generate over all metadata.
    for _, cur_cat_dir in enumerate(cat_dirs):
      cur_cat_name = os.path.basename(cur_cat_dir.strip("/"))
      cur_fns = tools.list_files(cur_cat_dir, img_exts)
      print("{} has image: {}".format(cur_cat_dir, len(cur_fns)))
      all_cat_names = [cur_cat_name] * len(cur_fns)
      all_data.extend(zip(cur_fns, all_cat_names))

    save_dir = self.ds_info.get_value(DatasetInfoKey.SAVE_DIR)
    os.makedirs(save_dir, exist_ok=True)
    meta_fn = os.path.join(save_dir, "all.csv")
    with open(meta_fn, "w") as f:
      writer = csv.writer(f)
      writer.writerows(all_data)
      print("all metadata has been written to file: {}".format(meta_fn))
    # split data.
    self.split_metadata(meta_fn, train_ratio)

  def split_metadata(self, meta_fn, train_ratio=0.7, target_label_col=1):
    """Split metadata into train and test files.

    Returns:
      train meta fn, test meta fn, label id to name mapper, label name to id mapper.
    """
    assert not self.is_multi_label()
    # read metadata.
    cls_ids = {}
    label_names = {}
    label_ids = {}
    train_rows = []
    test_rows = []
    all_rows = []
    col_num = 0
    print("split data from {}".format(meta_fn))
    with open(meta_fn, "r") as f:
      reader = csv.reader(f)
      next(reader)
      cnt = 0
      for row in reader:
        col_num = len(row)
        all_rows.append(row)
        cur_label = row[int(target_label_col)]
        if cur_label not in cls_ids.keys():
          cur_id = len(label_names)
          label_ids[cur_label] = cur_id
          label_names[cur_id] = cur_label
          cls_ids[cur_label] = []
        cls_ids[cur_label].append(cnt)
        cnt += 1
    # shuffle and split.
    for _, ids in cls_ids.items():
      random.shuffle(ids)
      train_sz = int(len(ids) * train_ratio)
      train_ids = ids[:train_sz]
      test_ids = ids[train_sz:]
      train_rows.extend([all_rows[x] for x in train_ids])
      test_rows.extend([all_rows[x] for x in test_ids])
    # save mappers.
    self.ds_info.set_value(DatasetInfoKey.LABEL_ID_TO_NAME, label_names)
    self.ds_info.set_value(DatasetInfoKey.LABEL_NAME_TO_ID, label_ids)
    # save to separate metadata files.
    # training data.
    save_dir = self.ds_info.get_value(DatasetInfoKey.SAVE_DIR)
    train_meta_fn = os.path.join(save_dir, "train.csv")
    self.ds_info.set_value(DatasetInfoKey.TRAIN_META_FN, "train.csv")
    with open(train_meta_fn, "w") as f:
      writer = csv.writer(f)
      writer.writerow(tuple(["header"] * col_num))
      writer.writerows(train_rows)
      print(
          "train metadata has been written to file: {}".format(train_meta_fn))
      self.ds_info.set_value(DatasetInfoKey.TRAIN_SAMPLE_COUNT,
                             len(train_rows))
    # testing data.
    test_meta_fn = os.path.join(save_dir, "test.csv")
    self.ds_info.set_value(DatasetInfoKey.TEST_META_FN, "test.csv")
    with open(test_meta_fn, "w") as f:
      writer = csv.writer(f)
      writer.writerow(tuple(["header"] * col_num))
      writer.writerows(test_rows)
      print("test metadata has been written to file: {}".format(test_meta_fn))
      self.ds_info.set_value(DatasetInfoKey.TEST_SAMPLE_COUNT, len(test_rows))
    self.ds_info.save_info()

  @abc.abstractmethod
  def build_from_metadata(self,
                          meta_fn,
                          data_type,
                          target_img_height=256,
                          target_img_width=256,
                          save_fn_prefix=None):
    """Load dataset from metadata file and convert it to compact data format.

    The data format depends on the library of selection.

    Args:
      meta_fn: metadata file.
      data_type: train or test.
      save_fn_prefix: prefix for saved data file.
    """
    pass

  @abc.abstractmethod
  def build_from_folder(self, data_folder):
    """Create data from a given folder which has a set of category subfolders.
    """
    pass

  """ Fetch data from dataset. """

  @abc.abstractmethod
  def gen_batch_data(self,
                     data_type=commons.DataType.TRAIN,
                     batch_size=32,
                     target_img_height=128,
                     target_img_width=128,
                     preprocess_fn=None):
    """Create batch data for classification use.

    The data is not exposed to external but used in learner.
    """
    pass
