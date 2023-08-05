'''
@author: KaueBonfim
'''

import json
import pytesseract as ocr
from PIL import Image
import pyautogui
import pandas

def imagem_para_caracter(imagem:str):
    imagem=imagem.replace("\\", "/")
    im=Image.open(imagem)
    return ocr.image_to_string(im,lang='eng')

def pegarConteudo(NomeArquivo,leitura=None):
    arquivo = open(NomeArquivo, 'r')
    if(leitura==None):
        lista = arquivo.read()
    elif(leitura=="linha"):
        lista=arquivo.readlines()
    arquivo.close()
    return lista

def receber_texto_usuario(descricao):
    return pyautogui.prompt(text=descricao, title='prompt' , default='')

def tela_texto(xi:int, yi:int, xf:int, yf:int,path_arquivo,renderizacao=False,y=100,x=500)->str:
    result=lambda a,b:b-a 
    xd=result(xi,xf)
    yd=result(yi,yf)
    nome=path_arquivo.replace("\\", "/")
    xd=xf-xi
    yd=yf-yi
    #print(xi,yi,xd,yd)
    pyautogui.screenshot(nome,region=(xi,yi,xd,yd))
    if(renderizacao==True):
        im = Image.open(nome)
        ims=im.resize((x, y),Image.ANTIALIAS)
        ims.save(nome,'png')
    im=Image.open(nome)
    return ocr.image_to_string(im,lang='eng')

def alinharImagem(imagem,x,y):
    im = Image.open(imagem)
    ims=im.resize((x, y),Image.ANTIALIAS)
    ims.save(imagem,'png')
    
def pegarConteudoJson(NomeArquivo):
    
    arquivo = open(NomeArquivo, 'r')
    lista = arquivo.read()
    arquivo.close()    
    listat=json.loads(lista)  
    return dict(listat)

def pegarConteudoJsonDF(NomeArquivo):
    valor=pandas.read_json(NomeArquivo)  
    valor=pandas.DataFrame(valor)
    return valor

def pegarConteudoCSVDF(NomeArquivo:str):
    valor=pandas.read_csv(NomeArquivo)
    valor=pandas.DataFrame(valor)
    return valor
    
def pegarConteudoXLSDF(NomeArquivo:str,Planilha:str):
    valor=pandas.read_excel(NomeArquivo,sheet_name=Planilha)
    valor=pandas.DataFrame(valor)
    return valor

def DF_para_Dict(DataFarame):
    return DataFarame.to_dict()

def DF_para_String(DataFarame):
    return DataFarame.to_string()

def Data_Frame(dado):
    return pandas.DataFrame(dado)