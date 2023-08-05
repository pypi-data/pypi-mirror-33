'''
@author: KaueBonfim
'''
import pyautogui

from pynput.mouse import Listener
from  urllib import request
from bs4 import BeautifulSoup
import re

def tamanhoTela():
    return pyautogui.size()

def pegar_clique():
    def on_click(x, y, button, pressed):
        print('{0}{1}'.format('' if  pressed else '',(x, y)))
    with Listener(on_click=on_click) as listener:
        listener.join()    

def localizacao_imagem(imagem):  
    return pyautogui.locateOnScreen(imagem)

def localizacao_centro_imagem(imagem):
    return pyautogui.locateCenterOnScreen(imagem)

def localiza_todas_imagens(imagem):
    return list(pyautogui.locateAllOnScreen(imagem))

def inspecionar_html(url):
    response=request.urlopen(url)
    valor=response.read()
    soup=BeautifulSoup(valor,'html.parser')
    return soup

def html_tag(url,tag):
    response=request.urlopen(url)
    valor=response.read()
    soup=BeautifulSoup(valor,'html.parser')
    return soup

def valor_tag(url,tag,atributo):
    dicionario=[]
    tamanho=len(atributo)
    response=request.urlopen(url)
    valor=response.read()    
    soup=BeautifulSoup(valor,'html.parser')
    for line in soup.find_all(tag):
        if(re.search(str(atributo)+'="', str(line)) is not None):
            comeco=tamanho+2+int(str(line).find(str(atributo)+'="'))
            fim=int(str(line).find('"',comeco))
            dicionario.append((str(line)[comeco:fim],line))
    return dicionario     
    
