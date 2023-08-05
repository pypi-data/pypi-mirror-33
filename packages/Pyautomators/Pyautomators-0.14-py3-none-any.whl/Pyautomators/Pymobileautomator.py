'''
@author: KaueBonfim
'''

from appium import webdriver as mob
from Pyautomators.Pyelementautomator import Pyelement
import time
from Pyautomators.Pykeymouseautomator import Pykeymouseautomator
from selenium.webdriver import TouchActions

class Mobile(Pyelement,Pykeymouseautomator):
    def __init__(self,dicionario_caps,endereco='http://127.0.0.1:4723/wd/hub'):
        time.sleep(2)
        desired_caps = {}
        desired_caps=dicionario_caps
        self.driver= mob.Remote(command_executor=endereco,desired_capabilities=desired_caps) 
        self.touch=TouchActions(self.driver)      
        
    def fechar_programa(self):
        self.driver.close()
                
    def pressionar(self,elemento,tipo):
        element=self.elemento(elemento,tipo)   
        self.touch.tap(element)
        
    def arrastar_elemento(self,elemento1_tipo:tuple,elemento2_tipo:tuple):
        elemento1=self.elemento(elemento1_tipo[0],elemento1_tipo[1])
        elemento2=self.elemento(elemento2_tipo[0],elemento2_tipo[1])
        self.driver.drag_and_drop(elemento1,elemento2)
        
    def voltar(self):
        self.driver.back()
    
    def rolagem(self,elemento1_tipo:tuple,elemento2_tipo:tuple):
        elemento1=self.elemento(elemento1_tipo[0],elemento1_tipo[1])
        elemento2=self.elemento(elemento2_tipo[0],elemento2_tipo[1])
        self.driver.scroll(elemento1, elemento2)