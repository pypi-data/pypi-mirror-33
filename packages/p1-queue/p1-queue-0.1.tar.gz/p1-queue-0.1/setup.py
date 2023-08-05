from setuptools import setup, find_packages

setup(name='p1-queue',
      version='0.1',
      description='Messaging abstraction for AMQP',
      author='Turfa Auliarachman',
      author_email='turfa_auliarachman@rocketmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=['pika'],
      zip_safe=False,
      include_package_data=True)
