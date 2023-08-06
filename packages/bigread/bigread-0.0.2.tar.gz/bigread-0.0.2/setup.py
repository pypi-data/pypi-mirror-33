from setuptools import setup

setup (
  name='bigread',
  version='0.0.2',
  packages=['bigread'],
  keywords = ['text-mining', 'large-files', 'streaming'],
  description='Stream huge files with minimal RAM usage',
  url='https://github.com/duhaime/bigread',
  author='Douglas Duhaime',
  author_email='douglas.duhaime@gmail.com',
  license='MIT',
  install_requires=[
    'six==1.11.0',
  ],
)
