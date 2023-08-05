"""Keras version of image classification dataset.
"""

import csv
import h5py
import math
import os
import random
import time
import PIL.Image

import cv2

import numpy as np
from tqdm import tqdm

from keras.utils import to_categorical

from visualdata.shared import commons, tools
from visualdata.image.shared.tools import read_img_data
from visualdata.image.classification import DatasetInfoKey
from visualdata.image.classification import Dataset as ImgClfDataset


class Dataset(ImgClfDataset):
  """Keras implementation of image classification dataset.
  """

  def __init__(self, save_dir, ds_info=None):
    """Init for keras dataset.
    """
    super(Dataset, self).__init__(save_dir, ds_info)
    self.ds_info.set_value(DatasetInfoKey.ENGINE, "keras")

  def build_from_metadata_single_label(self,
                                       data_type,
                                       target_img_height=256,
                                       target_img_width=256):
    """Build single label data.
    """
    # set data filenames.
    assert data_type in [commons.DataType.TRAIN, commons.DataType.TEST]
    data_fn = ""
    meta_fn = ""
    if data_type == commons.DataType.TRAIN:
      meta_fn = "train.csv"
      data_fn = "train.h5"
      self.ds_info.set_value(DatasetInfoKey.TRAIN_DATA_FN, data_fn)
    else:
      meta_fn = "test.csv"
      data_fn = "test.h5"
      self.ds_info.set_value(DatasetInfoKey.TEST_DATA_FN, data_fn)
    meta_fn = os.path.join(self.ds_info.save_dir, meta_fn)
    data_fn = os.path.join(self.ds_info.save_dir, data_fn)
    if not os.path.exists(data_fn):
      # convert metadata to data file.
      # read all metadata.
      label_names = {}
      label_ids = {}
      img_fns = []
      labels = []
      print("converting {}".format(meta_fn))
      with open(meta_fn, "r") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
          assert len(row) == 2
          img_fns.append(row[0])
          if row[1] not in label_ids:
            cur_label_id = len(label_ids)
            label_ids[row[1]] = cur_label_id
            label_names[cur_label_id] = row[1]
          labels.append(label_ids[row[1]])
      self.ds_info.set_value(DatasetInfoKey.LABEL_ID_TO_NAME, label_names)
      self.ds_info.set_value(DatasetInfoKey.LABEL_NAME_TO_ID, label_ids)
      # read image and convert to file.
      with h5py.File(data_fn, "w", libver="latest") as f:
        # create dataset structure.
        img_dset = f.create_dataset(
            "images",
            shape=(0, target_img_height, target_img_width, 3),
            dtype=np.uint8,
            maxshape=(None, target_img_height, target_img_width, 3))
        label_dset = f.create_dataset(
            "labels", shape=(0, ), dtype=np.int16, maxshape=(None, ))
        # add each image and label.
        for img_id, img_fn in enumerate(tqdm(img_fns)):
          img_data = read_img_data(img_fn,
                                   (target_img_height, target_img_width))
          if img_data is not None:
            # img_data = np.swapaxes(img_data, 0, 1)
            img_dset.resize(img_dset.len() + 1, axis=0)
            img_dset[-1] = img_data
            label_dset.resize(label_dset.len() + 1, axis=0)
            label_dset[-1] = labels[img_id]
        print("metadata {} has been converted to data file: {}".format(
            meta_fn, data_fn))
        if data_type == commons.DataType.TRAIN:
          self.ds_info.set_value(DatasetInfoKey.TRAIN_SAMPLE_COUNT,
                                 img_dset.len())
        else:
          self.ds_info.set_value(DatasetInfoKey.TEST_SAMPLE_COUNT,
                                 img_dset.len())
        self.ds_info.save_info()

  def build_from_metadata_multi_label(self,
                                      data_type,
                                      target_img_height=256,
                                      target_img_width=256):
    """Build multi-label data.

    Format: img_fn, label_val1, label_val2, ...
    """
    # set data filenames.
    assert data_type in [commons.DataType.TRAIN, commons.DataType.TEST]
    data_fn = ""
    if data_type == commons.DataType.TRAIN:
      self.ds_info.set_value(DatasetInfoKey.TRAIN_DATA_FN, data_fn)
    else:
      self.ds_info.set_value(DatasetInfoKey.TEST_DATA_FN, data_fn)
    if not os.path.exists(data_fn):
      # read all metadata.
      label_names = {}
      label_ids = {}
      img_fns = []
      labels = []  # two dimension list.
      print("converting {}".format(meta_fn))
      with open(meta_fn, "r") as f:
        reader = csv.reader(f)
        # ignore title.
        next(reader)
        for row in reader:
          labels.append([])
          img_fns.append(row[0])
          for cur_label_name in row[1:]:
            if cur_label_name not in label_ids:
              cur_label_id = len(label_ids)
              label_ids[cur_label_name] = cur_label_id
              label_names[cur_label_id] = cur_label_name
            labels[-1].append(cur_label_id)
      self.ds_info.set_value(DatasetInfoKey.LABEL_ID_TO_NAME, label_names)
      self.ds_info.set_value(DatasetInfoKey.LABEL_NAME_TO_ID, label_ids)
      # read image and convert to file.
      with h5py.File(data_fn) as f:
        # create dataset.
        img_dset = f.create_dataset(
            "images",
            shape=(0, 256, 256, 3),
            dtype=np.uint8,
            maxshape=(None, 256, 256, 3))
        # binary matrix, each label id will be set to 1.
        label_dset = f.create_dataset(
            "labels",
            shape=(0, len(label_ids)),
            dtype=np.uint8,
            maxshape=(None, len(label_ids)))
        # fill datasets.
        for img_id, img_fn in enumerate(tqdm(img_fns)):
          # img_obj = DeepImage(img_fn)
          img_data = None
          if img_data is not None:
            # make (height, weight, channel)
            img_data = np.swapaxes(img_data, 0, 1)
            img_dset.resize(img_dset.len() + 1, axis=0)
            img_dset[-1] = img_data
            # form label vector.
            label_dset.resize(label_dset.len() + 1, axis=0)
            cur_label_vec = np.zeros(len(label_ids), dtype=np.uint8)
            for cur_sublabel in labels[img_id]:
              cur_label_vec[cur_sublabel] = 1
            label_dset[-1] = cur_label_vec
        print("metadata {} has been converted to data file: {}".format(
            meta_fn, data_fn))
        if data_type == commons.DataType.TRAIN:
          self.ds_info.set_value(DatasetInfoKey.TRAIN_SAMPLE_COUNT,
                                 img_dset.len())
        else:
          self.ds_info.set_value(DatasetInfoKey.TEST_SAMPLE_COUNT,
                                 img_dset.len())
        self.ds_info.save_info()

  def build_from_metadata(self,
                          data_type,
                          target_img_height=256,
                          target_img_width=256):
    """Convert dataset meta file to data file.
    """
    if self.is_multi_label():
      self.build_from_metadata_multi_label(
          data_type,
          target_img_height=target_img_height,
          target_img_width=target_img_width)
    else:
      self.build_from_metadata_single_label(
          data_type,
          target_img_height=target_img_height,
          target_img_width=target_img_width)

  def build_from_folder(self, data_folder, train_ratio=0.8):
    """Implementation to build data from folder.
    """
    assert not self.is_multi_label(
    ), "build from folder only supports single label."
    # create metadata.
    self.gen_metadata_from_folder(data_folder, train_ratio=train_ratio)
    # convert to hdf5.
    self.build_from_metadata(commons.DataType.TRAIN, 224, 224)
    self.build_from_metadata(commons.DataType.TEST, 224, 224)

  def gen_batch_data(self,
                     data_type=commons.DataType.TRAIN,
                     batch_size=32,
                     target_img_height=128,
                     target_img_width=128,
                     preprocess_fn=None):
    """Create batch image generator for keras model.

    Used as a data generator.

    Returns:
      a batch data generator.
    """
    # init random.
    random.seed(time.time())
    data_fn = None
    samp_count = 0
    if data_type == commons.DataType.TRAIN:
      data_fn = "train.h5"
      samp_count = self.ds_info.get_value(DatasetInfoKey.TRAIN_SAMPLE_COUNT)
    else:
      data_fn = "test.h5"
      samp_count = self.ds_info.get_value(DatasetInfoKey.TEST_SAMPLE_COUNT)
    data_fn = os.path.join(self.ds_info.save_dir, data_fn)
    print("\nreading from data file: {}".format(data_fn))
    print("sample count: {}".format(samp_count))
    while True:
      assert os.path.exists(data_fn)
      print("\nstart data file for new epoch...")
      with h5py.File(data_fn, "r") as f:
        img_dset = f["images"]
        label_dset = f["labels"]
        samp_ids = list(range(samp_count))
        random.shuffle(samp_ids)
        num_batches = int(math.ceil(samp_count * 1.0 / batch_size))
        print("number of batches: {}".format(num_batches))
        for idx in range(num_batches):
          startt = time.time()
          # select current batch.
          if idx == num_batches - 1:
            batch_indice = samp_ids[idx * batch_size:]
          else:
            batch_indice = samp_ids[idx * batch_size:
                                    idx * batch_size + batch_size]
          batch_indice = sorted(batch_indice)
          img_batch = img_dset[batch_indice]
          label_batch = label_dset[batch_indice]
          # TODO(jiefeng): resize images.
          # preprocessing.
          if preprocess_fn is not None:
            new_batch = []
            for img_id, img_arr in enumerate(img_batch):
              new_arr = preprocess_fn(img_arr)
              new_batch.append(new_arr)
            img_batch = np.array(new_batch)
          # convert type.
          img_batch = img_batch.astype(np.float32)
          if not self.is_multi_label():
            label_batch = to_categorical(
                label_batch,
                len(self.ds_info.get_value(DatasetInfoKey.LABEL_NAME_TO_ID)))
          # print "label batch shape: {}".format(label_batch.shape)
          yield (img_batch, label_batch)


if __name__ == "__main__":
  dataset = Dataset("test", "./")
