'''
@author: KaueBonfim
'''
import pyautogui
from  assertpy import assert_that
from time import sleep
from Pyautomators.Pykeymouseautomator import Pykeymouseautomator

def verifica_tela(path_imagem:str)->bool:
    if(pyautogui.locateOnScreen(image=path_imagem)):
        return True
    else:
        return False
    
def verifica_valor(valor,tipo:str,comparado=None)->bool:
    retorno="Inserir um tipo correto"
    if(tipo=="igual"):
        retorno=assert_that(valor).is_equal_to(comparado)
    elif(tipo=="verdadeiro"):
        retorno=assert_that(valor).is_true()
    elif(tipo=="diferente"):
        retorno=assert_that(valor).is_not_equal_to(comparado)
    elif(tipo=="falso"):
        retorno=assert_that(valor).is_false()
    elif(tipo=="contem"):
        retorno=assert_that(valor).contains(comparado)
    elif(tipo=="vazio"):
        retorno=assert_that(valor).is_empty()
    return retorno

def aguardar_tela(imagem,tentativa=1,tempo=0.1,valida=False,agir=False,acao=None,valor:tuple=None):
    validador=False
    for ponto in range(tentativa):
        
        result=pyautogui.locateOnScreen(imagem)
        if(result  is not None):
            validador=True
            break
        
        elif(agir==True):
            if(acao=="clica"):
                if(valor is not None):
                    Pykeymouseautomator.clica_coordenada(*valor)
            if(acao=="digita"):                
                if(valor is not None):
                    Pykeymouseautomator.digitos(*valor)
            if(acao=="escreve"):
                if(valor is not None):
                    Pykeymouseautomator.escrever_direto(*valor)
            if(acao=="mover"):
                if(valor is not None):
                    Pykeymouseautomator.moverMouse(*valor)
            if(acao=="digitos"):
                if(valor is not None):
                    Pykeymouseautomator.combo_digitos(*valor)
            if(acao=="mantenha"):
                if(valor is not None):
                    Pykeymouseautomator.mantenha_e_digite(*valor)
        sleep(tempo)
    if(valida):
        assert_that(validador).is_true()
    return result
