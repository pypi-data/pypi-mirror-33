"""Tests for keras based dataset api.
"""

import visualdata as vd

data_dir = "/media/jiefeng/Data/datahouse/Recognition/CALTECH101/dataset"


def build_dataset():
  dataset = vd.image.classification.keras.Dataset(data_dir)
  dataset.build_from_folder(
      "/media/jiefeng/Data/datahouse/Recognition/CALTECH101/selected_data")


def gen_batches():
  dataset = vd.image.classification.keras.Dataset(data_dir)
  train_data_gen = dataset.gen_batch_data(batch_size=8)
  imgs, labels = next(train_data_gen)
  print(imgs.shape)
  print(labels.shape)
  print(labels)


if __name__ == "__main__":
  build_dataset()
  # gen_batches()
