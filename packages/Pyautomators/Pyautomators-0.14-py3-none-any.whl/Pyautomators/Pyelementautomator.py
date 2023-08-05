'''
@author: KaueBonfim
'''
from Pyautomators.Pysearchelementautomator import Element

class Pyelement(Element):
     
    def escreve(self,elemento,conteudo,tipo=None):
        element=self.elemento(elemento,tipo) 
        element.send_keys(conteudo)
        return element
        

    def clica(self,elemento,tipo=None):
        element=self.elemento(elemento,tipo) 
        element.click()
        return element
             
    
    def pegar_texto(self,elemento,tipo):
        element=self.elemento(elemento,tipo) 
        return element.text
            
    def confirmar(self):
        try:
            self.submit()
        except:
            print('Nenhum elemento foi encontrado')
            
    def escrever_elemento_lista(self,elemento,conteudo,tipo,indice_lista:int):
        element=self.elementos_list(elemento,tipo,indice_lista)
        element.send_keys(conteudo)
        return element      
            
    def clica_elemento_lista(self,elemento,tipo,indice_lista:int):
        element=self.elementos_list(elemento,tipo,indice_lista)
        element.click()
        return element 
    
    def pegar_texto_list(self,elemento,tipo,indice_lista:int):
        element=self.elementos_list(elemento,tipo,indice_lista)
        return element.text
    
    