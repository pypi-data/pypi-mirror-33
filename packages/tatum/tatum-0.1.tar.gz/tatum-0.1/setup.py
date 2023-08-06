from setuptools import setup

with open("README.md", "r") as fh:
  long_description = fh.read()

setup(name='tatum',
      version='0.1',
      description='A Simple Chaining Wrapper for PyMongo Aggregated Queries',
      url='http://github.com/sheeloroee/tatum',
      classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        "Operating System :: OS Independent"
      ],
      keywords='nosql mongo pymongo mongodb queries chaining aggregation wrapper db',
      author='SheeloRoee',
      author_email='roee.sheelo@gmail.com',
      license='MIT',
      packages=['tatum'],
      include_package_data=True,      
      zip_safe=False)