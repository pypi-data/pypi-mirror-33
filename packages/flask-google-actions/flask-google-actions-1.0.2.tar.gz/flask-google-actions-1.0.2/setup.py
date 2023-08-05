from setuptools import setup

setup(name='flask-google-actions',
      version='1.0.2',
      description='Client library for Actions on Google using python and flask',
      url='https://github.com/caycewilliams/flask-actions-on-google-python',
      author='Cayce Williams',
      author_email='caycewilliams77@gmail.com',
      license='MIT',
      packages=['flaskactions'],
      install_requires=[
          'google-actions==1.0.0',
          'flask',
          'flask-basicauth'],
      zip_safe=False)
