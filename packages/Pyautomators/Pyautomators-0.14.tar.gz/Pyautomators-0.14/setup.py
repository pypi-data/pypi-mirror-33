# -*- coding: utf-8 -*-
from setuptools import setup,find_packages

setup(name='Pyautomators',
      version='0.14',
      url='https://github.com/kauebonfimm/Pyautomators',
      license='MIT',
      author='KaueBonfim',
      author_email='kaueoliveir95@hotmail.com',
      description='Biblioteca de automação para geracao completa de ambientacao de testes',
      packages=['Pyautomators'],
	  install_requires=["pytesseract","pillow","pyautogui","assertpy","cx_Oracle","selenium","pytractor","numpy","mysqlclient","opencv-python","Appium-Python-Client","pynput","behave2cucumber","python-jenkins","behave","django","pandas","pymongo","beautifulsoup4","nltk","TestLink-API-Python-client","sqlalchemy","argparse"],
      zip_safe=True)
	  


