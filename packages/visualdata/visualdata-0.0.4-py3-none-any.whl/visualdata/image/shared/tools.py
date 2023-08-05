"""Image tools.
"""

import os

from deepimage import DeepImage


def read_img_data(img_path, target_img_size=(256, 256), use_gray=False):
  """Read image data to ndarray.
  """
  img_obj = None
  if os.path.exists(img_path):
    img_obj = DeepImage(fp=img_path)
  else:
    img_obj = DeepImage(url=img_path)
  img_obj.resize(target_img_size)
  return img_obj.to_array()
