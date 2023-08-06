from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='pfla',
      version='0.0.7',
      description='Python facial landmarking and analysis',
      long_description='Annotate anteroposterior digital images and run statistical analyses on resulting matrices',
      classifiers=[
	'Programming Language :: Python :: 3.5',
	'Topic :: Scientific/Engineering :: Medical Science Apps.',
	'Topic :: Scientific/Engineering :: Image Recognition'
	],
      url='https://github.com/maxrousseau/pfla',
      author='Maxime Rousseau',
      author_email='maximerousseau08@gmail.com',
      scripts=['bin/pfla'],
      include_package_data=True,
      license='MIT',
      packages=['pfla'],
      install_requires=['dlib','imutils','numpy','argparse','pandas','rpy2',
                       'progress'],
      zip_safe=False)
