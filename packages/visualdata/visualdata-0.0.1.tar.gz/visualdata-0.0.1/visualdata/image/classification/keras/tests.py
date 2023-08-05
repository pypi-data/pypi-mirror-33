"""Tests for keras based dataset api.
"""

import visualdata as vd


def build_dataset():
  dataset = vd.image.classification.keras.Dataset(
      "/Users/jiefeng/dev/data/scanned/facing/dataset")
  dataset.build_from_folder("/Users/jiefeng/dev/data/scanned/facing/train")


def gen_batches():
  data_dir = "/Users/jiefeng/dev/data/scanned/facing/dataset"
  dataset = vd.image.classification.keras.Dataset(data_dir)
  train_data_gen = dataset.gen_batch_data(batch_size=16)
  imgs, labels = next(train_data_gen)
  print(imgs.shape)
  print(labels.shape)


if __name__ == "__main__":
  # build_dataset()
  gen_batches()
