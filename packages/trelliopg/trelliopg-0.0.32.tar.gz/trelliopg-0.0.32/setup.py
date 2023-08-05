from setuptools import setup

setup(name='trelliopg',
      version='0.0.32',
      author='Abhishek Verma, Nirmal Singh',
      author_email='ashuverma1989@gmail.com, nirmal.singh.cer08@itbhu.ac.in',
      url='https://github.com/zoniclabs/trelliopg',
      description='A fast database connector and micro-orm for postgresql',
      packages=['trelliopg'],
      install_requires=['asyncpg'])
