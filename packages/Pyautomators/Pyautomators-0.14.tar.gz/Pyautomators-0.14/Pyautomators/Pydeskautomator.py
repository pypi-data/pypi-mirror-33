'''
@author: KaueBonfim
'''
import os 
from selenium import webdriver 
from Pyautomators.Pyelementautomator import Pyelement
from Pyautomators.Pykeymouseautomator import Pykeymouseautomator

class Desk(Pyelement,Pykeymouseautomator):
    def __init__(self,caminho_driver:str,aplicacao:str):
        os.startfile(caminho_driver+"Winium.Desktop.Driver.exe")
        self.driver= webdriver.Remote(command_executor="http://localhost:9999",desired_capabilities={"app": aplicacao})
        
    def fechar_programa(self):
        self.driver.close()
        os.system("TASKKILL /IM Winium.Desktop.Driver.exe")
        
        