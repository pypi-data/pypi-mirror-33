'''
@author: KaueBonfim
'''

class Element():
    '''
    classdocs
    '''

    def elemento(self,elemento,tipo):
        if(tipo == 'id'):
            element=self.driver.find_element_by_id(elemento)
        elif(tipo == 'name'):
            element=self.driver.find_element_by_name(elemento) 
        elif(tipo == 'class'):            
            element=self.driver.find_element_by_class_name(elemento) 
        elif(tipo == 'xpath'):            
            element=self.driver.find_element_by_xpath(elemento) 
        elif(tipo == 'link'):            
            element=self.driver.find_element_by_link_text(elemento) 
        elif(tipo == 'tag'):            
            element=self.driver.find_element_by_tag_name(elemento) 
        elif(tipo == 'css'):            
            element=self.driver.find_element_by_css_selector(elemento) 
        elif(tipo == 'text'):            
            element=self.driver.find_element_by_partial_link_text(elemento) 
        elif(tipo=='android'):
            element=self.driver.find_element_by_android_uiautomator(elemento) 
        elif(elemento=='ios'):
            element=self.driver.find_element_by_ios_uiautomation(elemento)
        else:
            print('nenhum elemento foi especificado')
        return element
      
    def elemento_list(self,elemento,tipo,indice_lista):
        if(tipo == 'id'):           
            elements=self.driver.find_elements_by_id(elemento)  
        elif(tipo == 'name'):
            elements=self.driver.find_elements_by_name(elemento)
        elif(tipo == 'class'):            
            elements=self.driver.find_elements_by_class_name(elemento)
        elif(tipo == 'xpath'):            
            elements=self.driver.find_elements_by_xpath(elemento)
        elif(tipo == 'link'):            
            elements=self.driver.find_elements_by_link_text(elemento)
        elif(tipo == 'tag'):            
            elements=self.driver.find_elements_by_tag_name(elemento)
        elif(tipo == 'text'):            
            elements=self.driver.find_elements_by_partial_link_text(elemento)
        elif(tipo == 'css'):            
            elements=self.driver.find_elements_by_css_selector(elemento)
        elif(tipo=='binding'):
            elements=self.driver.find_elements_by_binding(elemento)
        elif(tipo=='model'):
            elements=self.driver.find_elements_by_model(elemento)
        else:
            print('nenhum elemento foi especificado')
        element=elements[indice_lista]
        return element
    
    def elementos_list(self,elemento,tipo,indice_lista):
        if(tipo == 'id'):           
            elements=self.driver.find_elements_by_id(elemento)  
        elif(tipo == 'name'):
            elements=self.driver.find_elements_by_name(elemento)
        elif(tipo == 'class'):            
            elements=self.driver.find_elements_by_class_name(elemento)
        elif(tipo == 'xpath'):            
            elements=self.driver.find_elements_by_xpath(elemento)
        elif(tipo == 'link'):            
            elements=self.driver.find_elements_by_link_text(elemento)
        elif(tipo == 'tag'):            
            elements=self.driver.find_elements_by_tag_name(elemento)
        elif(tipo == 'text'):            
            elements=self.driver.find_elements_by_partial_link_text(elemento)
        elif(tipo == 'css'):            
            elements=self.driver.find_elements_by_css_selector(elemento)
        elif(tipo=='binding'):
            elements=self.driver.find_elements_by_binding(elemento)
        elif(tipo=='model'):
            elements=self.driver.find_elements_by_model(elemento)
        else:
            print('nenhum elemento foi especificado')
        return elements