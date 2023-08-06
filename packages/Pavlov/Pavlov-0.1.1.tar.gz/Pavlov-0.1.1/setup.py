from setuptools import setup, find_packages

long_description = '''
Pavlov is a modular, composable reinforcement learning API,
with models written in Keras with a Tensorflow backend.

Use Pavlov if you want a reinforcement learning library that:
    - Allows for easy and fast composition of various
      algorithms, exploration strategies, and state preprocessors
    - Allows for arbitrarily defined custom network architectures
    - Works with any environment that follows the OpenAI Gym interface
    - Comes with its own Docker image for both GPU and CPU usage

Pavlov is distributed under the MIT license.
'''

setup(name='Pavlov',
      version='0.1.1',
      description='A modular reinforcement learning pipeline with Keras',
      long_description=long_description,
      author='Nash Taylor',
      author_email='nashtaylor22@gmail.com',
      url='https://github.com/ntaylorwss/pavlov',
      download_url='https://github.com/ntaylorwss/pavlov/tarball/0.1.0',
      license='MIT',
      packages=find_packages(),
      classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
      ])
