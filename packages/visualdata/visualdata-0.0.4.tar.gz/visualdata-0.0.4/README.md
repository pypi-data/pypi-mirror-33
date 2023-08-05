# VisualData

VisualData is a library to simplify how you work with image data. It is designed to be a standalone library although the experience is better when you use it with visualdata web app (https://www.visualdata.io).

## Datasets

The library contains dataset classes for some of the most popular machine learning libraries.

The following example shows how easy it is to create a dataset for training in Keras.

```python
import visualdata as vd

# create an image classification dataset for keras. Specify a directory to save data files.
clf_dataset = vd.image.classification.keras.Dataset(save_dir="")
# build dataset from folder.
clf_dataset.build_from_folder(folder_name)
# get batch data generator. It can be used directly in fit_generator.
clf_data_generator = clf_dataset.gen_batch_data(batch_size=32, target_img_size=(224, 224), preprocess_fn=None)

# create an image detection dataset for keras.
det_dataset = vd.image.detection.keras.Dataset(save_dir="")
# build dataset from metadata file.
det_dataset.build_from_metadata(meta_fn)
# get batch data generator.
det_data_generator = det_dataset.gen_batch_data(batch_size=32, target_img_size=(224, 224), preprocess_fn=None)
```
