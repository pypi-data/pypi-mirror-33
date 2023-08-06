from setuptools import setup
setup(name='m-schedule',
      version='0.1',
      description='Tạo schedule chạy theo lịch',
      url='https://github.com/mobiovn',
      author='MOBIO',
      author_email='contact@mobio.vn',
      license='MIT',
      packages=['mobio/libs/schedule'],
      install_requires=['m-singleton',
                        'schedule',
                        'm-threadpool'])
