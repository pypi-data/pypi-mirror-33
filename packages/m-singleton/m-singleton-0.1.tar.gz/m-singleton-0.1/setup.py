from setuptools import setup
setup(name='m-singleton',
      version='0.1',
      description='Setup normal class to SingletonClass',
      url='https://github.com/mobiovn',
      author='MOBIO',
      author_email='contact@mobio.vn',
      license='MIT',
      packages=['mobio/libs/Singleton'],
      install_requires=['numpy>=1.11',
                        'matplotlib>=1.5'])
