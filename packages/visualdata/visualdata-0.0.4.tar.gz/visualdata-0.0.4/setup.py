from setuptools import setup, find_packages

with open("./configs/requirements.txt", "r") as f:
  dep_packages = f.readlines()
  # remove local install.
  dep_packages = [x.strip() for x in dep_packages if not x.startswith("-e")]
  # remove unnecessary packages.
  dep_packages = [x for x in dep_packages if not x.startswith("certifi")]

setup(
    name="visualdata",
    version="0.0.4",
    description="library to manage image data",
    keywords="computer vision image",
    url="https://github.com/perceptance/visualdata-lib",
    author="Jie Feng",
    author_email="jiefengdev@gmail.com",
    packages=find_packages("./"),
    install_requires=dep_packages,
    extras_require={
        "tf": ["tensorflow>=1.0.0"],
        "tf_gpu": ["tensorflow-gpu>=1.0.0"],
    },
    include_package_data=True,
    zip_safe=False)
