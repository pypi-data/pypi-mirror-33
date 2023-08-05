import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(name='fxvol',
      version='0.1',
      description='poc in python for Lee extrapolation',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='',
      author='Jerome Petit',
      author_email='jerome.petit@misys.com',
      packages=setuptools.find_packages(),
      classifiers=(
      "Programming Language :: Python :: 3",
      "License :: OSI Approved :: MIT License",
      "Operating System :: OS Independent",
      ),
      zip_safe=False)