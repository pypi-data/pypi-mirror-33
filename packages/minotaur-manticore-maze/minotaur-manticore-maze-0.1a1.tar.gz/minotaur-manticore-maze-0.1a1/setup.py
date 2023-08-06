from setuptools import setup
from textwrap import dedent

long_description = dedent("""
    This is a text-based game where you navigate a maze and battle minotaurs
    and manticores. Along the way you will find interesting items and hidden
    areas that may improve your chances of success.
    """)

setup(
    name='minotaur-manticore-maze',
    version='0.1a1',
    description='A text-based game where you battle enemies in a maze.',
    long_description=long_description,
    url='https://github.com/smidem/minotaur-manticore-maze.git',
    author='Shane McGuckian',
    author_email='contact.smidem@gmail.com',
    license='MIT',
    packages=['minotaur-manticore-maze'],
    keywords=['fantasy text-based game'],
    classifiers=['Development Status :: 1 - Planning',
                 'Intended Audience :: Other Audience',
                 'License :: OSI Approved :: MIT License',
                 'Programming Language :: Python :: 3.6',
                 'Topic :: Games/Entertainment'],
    zip_safe=False,
    install_requires=['tqdm'])
