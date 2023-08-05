#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='tec.ic.ia.p2.g07.main',
      version='1.0.0',
      py_modules=['tec.ic','tec.ic.ia','tec.ic.ia.p2','tec.ic.ia.p2.g07','tec.ic.ia.p2.g07.main'],
      description='This repository contains the second project of Artificial Intelligence course from Instituto Tecnológico de Costa Rica, imparted by the professor Juan Manuel Esquivel. The project consists on some queries to search relations on a word database named "Etymological Wordnet" based by en.wiktionary.org.',
      author='Trifuerza',
      author_email='',
      url='https://github.com/mamemo/Etimology-Relationships',
      packages= find_packages(exclude=['docs', 'tests*']),
     )
