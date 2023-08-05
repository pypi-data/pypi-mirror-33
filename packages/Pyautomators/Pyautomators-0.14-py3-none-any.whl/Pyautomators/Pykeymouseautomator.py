'''
@author: KaueBonfim
'''

import pyautogui
class Pykeymouseautomator():
    @staticmethod
    def clica_coordenada(x,y,cliques=1,botao='left'):
        pyautogui.click(x,y,clicks=cliques,button=botao)
    @staticmethod
    def arraste_coordenada(xi,yi,xf,yf,botao="left",duracao=0.0):
        pyautogui.moveTo(x=xi,y=yi,duration=duracao)
        pyautogui.dragTo(x=xf,y=yf,button=botao,duration=duracao)
    @staticmethod
    def digitos(*digito):
        lista=[]
        if(type(digito)==tuple):
            for d in digito:
                if(type(d)==tuple):
                    for b in range(d[1]):
                        lista.append(d[0])
                else:
                    lista.append(d)
        pyautogui.press(lista,interval=0.5)
    @staticmethod
    def rolagemMouse(valor,x=None,y=None):
        pyautogui.moveTo(x, y)
        pyautogui.scroll(valor)
        
    @staticmethod
    def mantenha_e_digite(mantenha,digite):
        pyautogui.keyDown(mantenha)
        for digito in digite:
            pyautogui.press(digito)
        pyautogui.keyUp(mantenha)
    @staticmethod
    def combo_digitos(*teclas):
        pyautogui.hotkey(*teclas)
    @staticmethod
    def clica_imagem(path_imagem,clicks=1,botao='left'):
        x,y=pyautogui.locateCenterOnScreen(path_imagem)
        pyautogui.click(x,y,clicks=clicks,button=botao)
    @staticmethod    
    def escrever_direto(conteudo):
        pyautogui.typewrite(conteudo)
    @staticmethod    
    def moverMouse(x,y,duracao=0.0):
        pyautogui.moveTo(x,y,duration=duracao)    