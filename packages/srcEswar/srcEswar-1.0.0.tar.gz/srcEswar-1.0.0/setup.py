
import os
from distutils.command.register import register as register_orig
from distutils.command.upload import upload as upload_orig

from setuptools import setup


class register(register_orig):

    def _get_rc_file(self):
        return os.path.join('.', '.pypirc')

class upload(upload_orig):

    def _get_rc_file(self):
        return os.path.join('.', '.pypirc')

setup(
    name='srcEswar',
    version = '1.0.0',
    py_modules = ['eswar'],
    author = 'Eswar_123',
    author_email = 'eswar.kurakula99@gmail.com',
    cmdclass={
        'register': register,
        'upload': upload,
    }
)
