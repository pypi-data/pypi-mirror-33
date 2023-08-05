'''

@author: KaueBonfim
'''
import os 
from pytractor import webdriver as protactor
from selenium import webdriver
from Pyautomators.Pyelementautomator import Pyelement
from Pyautomators.Pykeymouseautomator import Pykeymouseautomator
from selenium.webdriver import ActionChains,common
from selenium.webdriver.support.ui import Select

class Web(Pyelement,Pykeymouseautomator):
    def __init__(self,driver,path_driver=None,options=None,Angular=False):
        
        if(Angular==True):
            if(driver == 'Chrome'):
                if(path_driver==None):
                    path_driver="chromedriver"
                self.driver=protactor.Chrome(executable_path=path_driver,chrome_options=options)
                
                    
            elif(driver == 'Firefox'):  
                if(path_driver==None):
                    path_driver="geckodriver"          
                self.driver=protactor.Firefox(str(path_driver),firefox_options=options)
                
                
            elif(driver == 'Ie'):    
                if(path_driver==None):
                    path_driver="IEDriverServer.exe"          
                self.driver=protactor.Ie(str(path_driver),ie_options=options)
        
        
            
        else:  
            if(driver == 'Chrome'):
                if(path_driver==None):
                    path_driver="chromedriver"
                self.driver=webdriver.Chrome(executable_path=path_driver,chrome_options=options)    
            elif(driver == 'Firefox'):  
                if(path_driver==None):
                    path_driver="geckodriver"          
                self.driver=webdriver.Firefox(executable_path=path_driver,firefox_options=options)
                
                
            elif(driver == 'Ie'):    
                if(path_driver==None):
                    path_driver="IEDriverServer.exe"          
                self.driver=webdriver.Ie(executable_path=path_driver,ie_options=options)
                
        self.acoes=ActionChains(self.driver)
        self.alerta=common.alert.Alert(self.driver)
    
    def fechar_programa(self):
        self.driver.quit()
        
        
    def url_atual(self):
        return self.driver.current_url
        
    def pagina(self,url):
        self.driver.get(url)
        
    def maximiza(self):
        self.driver.maximize_window()
    
    def preencher_tela(self):
        self.driver.fullscreen_window()
            
    def atualizar(self):
        self.driver.refresh()
        
    def voltar(self):
        self.driver.back()
    
    def frente(self):
        self.driver.forward()
    
    def limpar(self):
        self.driver.clear()
        
    def pegar_atributo(self,elemento,info):
        return elemento.get_attribute(info)
        
    def titulo(self):
        return self.driver.title
    
    def navegador(self):
        return self.driver.name
    
    def clica_mouse_elemento(self,elemento=None,tipo=None,botao=None):
        element=self.elemento(elemento,tipo) 
        if(botao=="direito"):
            self.acoes.context_click(element)
        elif(botao=="esquerdo"):
            self.acoes.click_and_hold(element)
        else:
            self.acoes.click(element)
        
    def arrastar_elemento(self,elemento1_tipo:tuple,elemento2_tipo:tuple):
        elemento1=self.elemento(elemento1_tipo[0],elemento1_tipo[1])
        elemento2=self.elemento(elemento2_tipo[0],elemento2_tipo[1])
        self.acoes.drag_and_drop(elemento1, elemento2)
        
    def arrastar_elemento_lista(self,elemento1_tipo_indice:tuple,elemento2_tipo_indice:tuple):
        elemento1=self.elementos_list(elemento1_tipo_indice[0],elemento1_tipo_indice[1],elemento1_tipo_indice[2])
        elemento2=self.elementos_list(elemento2_tipo_indice[0],elemento2_tipo_indice[1],elemento2_tipo_indice[2])
        self.acoes.drag_and_drop(elemento1, elemento2)
        
    def popUp_aceitar(self,aceitar:bool):
        if(aceitar==True):
            self.alerta.accept()
        elif(aceitar==False):
            self.alerta.dismiss()
        
    def popUp_autenticar(self,usuario,senha):
        self.alerta.authenticate(usuario,senha)
        
    def popUp_escrever(self,texto):
        self.alerta.send_keys(texto)
        
    def popUp_pegar_texto(self):
        return self.alerta.text
    
    def print_janela(self,path_imagem):
        self.driver.get_screenshot_as_file(path_imagem)
        
    def formulario_por_index(self,elemento,tipo,index):
        selecao=Select(self.elemento(elemento,tipo))
        selecao.select_by_index(index)
    
    def formulario_por_texto(self,elemento,tipo,text):
        selecao=Select(self.elemento(elemento,tipo))
        selecao.select_by_visible_text(text)
    
    def formulario_por_valor(self,elemento,tipo,value):
        selecao=Select(self.elemento(elemento,tipo))
        selecao.select_by_value(value)
        
    def formulario_vazio(self,elemento,tipo):
        selecao=Select(self.elemento(elemento,tipo))
        selecao.deselect_all()
        
    def formulario_index_livre(self,elemento,tipo,index):
        selecao=Select(self.elemento(elemento,tipo))
        selecao.deselect_by_index(index)
    
    def formulario_texto_livre(self,elemento,tipo,text):
        selecao=Select(self.elemento(elemento,tipo))
        selecao.deselect_by_visible_text(text)
    
    def formulario_valor_livre(self,elemento,tipo,value):
        selecao=Select(self.elemento(elemento,tipo))
        selecao.deselect_by_value(value)
        