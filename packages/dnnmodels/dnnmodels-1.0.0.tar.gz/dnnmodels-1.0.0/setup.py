from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='dnnmodels',
      version='1.0.0',
      url='https://github.com/NullConvergence/dnnmodels',
      download_url='https://github.com/NullConvergence/dnnmodels/archive/1.0.0.tar.gz',
      license='MIT',
      author='NullConvergence',
      author_email='nullconvergence@anonymous.ne',
      description="Simple models inspired by Cleverhans that help create DNN Architectures",
      install_requires=[
          'cleverhans',
          'tensorflow'
      ],
      packages=['dnnmodels'])
