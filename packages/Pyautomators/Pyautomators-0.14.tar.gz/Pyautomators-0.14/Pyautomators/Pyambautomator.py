'''
@author: KaueBonfim
'''
import os
import sys
import time
from collections import deque
import shutil
import http.server
import socketserver 


def irDiretorio(diretorio):
    diretorio=str(diretorio).replace("\\", "/")
    os.chdir(diretorio)

def criarPasta(nomePasta):
    os.mkdir('./'+nomePasta)

def abrirPrograma(programa):
    programa=str(programa).replace("\\", "/")
    return os.startfile(programa)

def terminal_parametro():
    return sys.argv    

def execute(command):
    os.system(command)
            
def servidor_http(endereco:str,porta:int):
    
    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer((endereco, porta), Handler)
    httpd.serve_forever()

def dia_mes_ano():
    line=time.localtime()
    line=list(line)
    lis=deque()
    for h in line:
        lis.appendleft(int(h))
        if(line.index(h) == 2):
            break
    return list(lis)

def caminho_ate_pasta():
    return str(str(os.path.dirname(os.getcwd())).replace("\\", "/")+"/")

def path_atual():
    return str(str(os.getcwd()).replace("\\", "/")+"/")

def copiar_aquivos_diretorio(path_arquivo1:str,path_arquivo2:str):
    path_arquivo1=str(path_arquivo1).replace("\\", "/")
    path_arquivo2=str(path_arquivo2).replace("\\", "/")
    shutil.copyfile(path_arquivo1, path_arquivo2)
    
def mover_arquivos_diretorio(path_arquivo1:str,path_arquivo2:str):
    path_arquivo1=str(path_arquivo1).replace("\\", "/")
    path_arquivo2=str(path_arquivo2).replace("\\", "/")
    shutil.move(path_arquivo1, path_arquivo2)
    
def gravar_em_arquivo(NomeArquivo,Conteudo):
    arquivo = open(NomeArquivo, 'w')
    arquivo.write(Conteudo)
    arquivo.close()
    
def criarArquivo(NomeArquivo):
    arquivo = open(NomeArquivo,"w")
    arquivo.close()
    
def remover_arquivo(NomeArquivo):
    os.remove(NomeArquivo)