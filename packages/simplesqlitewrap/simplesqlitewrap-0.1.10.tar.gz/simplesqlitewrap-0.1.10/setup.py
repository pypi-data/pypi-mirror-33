from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='simplesqlitewrap',
      version='0.1.10',
      description='Simple util from which I inherit my sqlite classes',
      long_description=long_description,
      long_description_content_type="text/markdown",
      # url='http://github.com/',
      author='zeroone2numeral2',
      license='MIT',
      packages=['simplesqlitewrap'],
      classifiers=(
      	"Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Database",
      ),
      zip_safe=False)