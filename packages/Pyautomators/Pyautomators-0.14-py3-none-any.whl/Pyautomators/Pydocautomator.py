'''
@author: KaueBonfim
'''
import pyautogui
import json
import behave2cucumber

def printarTela(path_arquivo):
    nome=path_arquivo.replace("\\", "/")
    pyautogui.screenshot(nome) 

def print_local(xi,yi,xf,yf,path_arquivo):
    result= lambda a,b:b-a 
    xd=result(xi,xf)
    yd=result(yi,yf)
    nome=path_arquivo.replace("\\", "/")    
    return pyautogui.screenshot(nome,region=(xi,yi, xd, yd))
   
def tranforma_cucumber(path_arquivo,novo):
    nome=path_arquivo.replace("\\", "/")
    with open(nome) as behave_json:
        cucumber_json = behave2cucumber.convert(json.load(behave_json))
        for element in cucumber_json:
            elemento=element["elements"]
            for lista in elemento:
                listaa=lista["steps"]
                for lis in listaa:
                    li=lis["result"]["duration"]
                    lis["result"]["duration"]=int(li*1000000000)
        arquivo = open(novo,'w')  
        conteudo=json.loads(str(cucumber_json).replace("'",'"'))
        conteudo=json.dumps(conteudo,indent=4)         
        arquivo.write(conteudo)
        arquivo.close()