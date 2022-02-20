from setuptools import setup, find_packages

setup(name="chat_server",
      version="1.0",
      description="mini_chat_server",
      author="Roman Popadin",
      author_email="r.popadin@noname.com",
      packages=find_packages(),
      install_requires=['PyQt5', 'argparse', 'binascii', 'configparser', 'dataclasses', 'datetime', 'hashlib', 'hmac',
                        'json', 'logging', 'os', 'select', 'socket', 'sqlalchemy', 'sqlalchemy.orm', 'sqlalchemy.sql',
                        'sqlite3', 'sys', 'threading']
      )