"""Base class for data.
"""

import abc
import json


class DatasetInfoKeyBase(object):
  """Dataset info key string name.
  """
  NAME = "name"
  SAVE_DIR = "save_dir"
  ENGINE = "engine"
  # metadata file for dataset.
  TRAIN_META_FN = "train_meta_fn"
  TEST_META_FN = "test_meta_fn"
  # actual data file for dataset. type varies depend on library.
  TRAIN_DATA_FN = "train_data_fn"
  TEST_DATA_FN = "test_data_fn"
  LABELS = "labels"
  TRAIN_SAMPLE_COUNT = "train_sample_count"
  TEST_SAMPLE_COUNT = "test_sample_count"
  # dict name mapping name to id.
  LABEL_NAME_TO_ID = "nametoid"
  # dict name mapping id to name.
  LABEL_ID_TO_NAME = "idtoname"


class DataSetInfoBase(object):
  """Base class for dataset information.

  Create common fields, read and write fields.
  """
  __metaclass__ = abc.ABCMeta

  # path to the file with metadata regarding the dataset, e.g. class labels, data file path.
  _info_fn = ""
  # object of dataset info.
  _ds_info = None

  def __init__(self, info_fn=None):
    self._info_fn = info_fn
    self._ds_info = {
        DatasetInfoKeyBase.ENGINE: None,
        DatasetInfoKeyBase.TRAIN_META_FN: "",
        DatasetInfoKeyBase.TEST_META_FN: "",
        DatasetInfoKeyBase.TRAIN_DATA_FN: "",
        DatasetInfoKeyBase.TEST_DATA_FN: "",
        # when extend to multiple labels, it will be a list.
        DatasetInfoKeyBase.LABELS: {
            DatasetInfoKeyBase.LABEL_ID_TO_NAME: {},
            DatasetInfoKeyBase.LABEL_NAME_TO_ID: {}
        },
        DatasetInfoKeyBase.TRAIN_SAMPLE_COUNT: 0,
        DatasetInfoKeyBase.TEST_SAMPLE_COUNT: 0
    }

  def save_info(self):
    """Save dataset info to a file
    """
    with open(self._info_fn, "w") as f:
      json.dump(self._ds_info, f)
    print("[{}] dataset info saved to file {}".format(self.__class__.__name__,
                                                      self._info_fn))

  def load_info(self):
    """Load dataset info from a file.
    """
    with open(self._info_fn, "r") as f:
      self._ds_info = json.load(f)
    print("[{}] dataset info loaded from file {}".format(
        self.__class__.__name__, self._info_fn))

  def get_value(self, key_name):
    """Retrieve info value from structure.
    """
    if key_name in [
        DatasetInfoKeyBase.NAME, DatasetInfoKeyBase.ENGINE,
        DatasetInfoKeyBase.SAVE_DIR, DatasetInfoKeyBase.LABELS,
        DatasetInfoKeyBase.TRAIN_META_FN, DatasetInfoKeyBase.TEST_META_FN,
        DatasetInfoKeyBase.TRAIN_DATA_FN, DatasetInfoKeyBase.TEST_DATA_FN,
        DatasetInfoKeyBase.TRAIN_SAMPLE_COUNT,
        DatasetInfoKeyBase.TEST_SAMPLE_COUNT
    ]:
      return self._ds_info[key_name]

  def set_value(self, key_name, val):
    """Set data info value.
    """
    if key_name in [
        DatasetInfoKeyBase.NAME, DatasetInfoKeyBase.ENGINE,
        DatasetInfoKeyBase.SAVE_DIR, DatasetInfoKeyBase.LABELS,
        DatasetInfoKeyBase.TRAIN_META_FN, DatasetInfoKeyBase.TEST_META_FN,
        DatasetInfoKeyBase.TRAIN_DATA_FN, DatasetInfoKeyBase.TEST_DATA_FN,
        DatasetInfoKeyBase.TRAIN_SAMPLE_COUNT,
        DatasetInfoKeyBase.TEST_SAMPLE_COUNT
    ]:
      self._ds_info[key_name] = val

  def get_label_name(self, label_id):
    label_id = str(label_id)
    return self.get_value(DatasetInfoKeyBase.LABEL_ID_TO_NAME)[label_id]

  def get_label_id(self, label_name):
    return self.get_value(DatasetInfoKeyBase.LABEL_NAME_TO_ID)[label_name]


class DatasetBase(object):
  """Base class representing a generic dataset.
  """
  __metaclass__ = abc.ABCMeta

  def download(self):
    """Download data to local storage.
    """
    pass

  # @abc.abstractmethod
  def create_base_data(self):
    """Create a basic structure of the data to work with.

    Examples like loading image data and labels to array
    before specific format for later use.
    For internal use.
    """
    pass
