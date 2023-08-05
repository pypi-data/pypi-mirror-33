'''
@author: KaueBonfim
'''

import os
import re
import sqlite3
import numpy
class Project(object):
    '''
    classdocs
    '''

    @staticmethod
    def Criar_Projeto(nome_projeto,diretorio=None):
        
        if(diretorio!=None):
            os.chdir(diretorio)
        
        os.mkdir(nome_projeto)
        
        os.chdir(nome_projeto)
        
        
        lista_pastas_principal=["bin","dados","docs","drivers","elementosImagem","features","lib","steps","tools","steps/unit_test","steps/models","features/reports"]
        for lin in lista_pastas_principal:
            os.mkdir(lin)
            
        text=open("__init__.py","w")
        text.close()
                
        text=open("tools/__init__.py","w")
        text.close()
        
        text=open("environment.py","w")
        text.writelines('\n"""\t\tPyautomator Framework de teste \n\n\t\t\t{}"""\n\n'.format(nome_projeto))
        text.writelines('from Pyautomators import *\nfrom time import sleep\n')
        text.writelines("def before_all(context):\n\tpass\n\n")
        text.writelines("def before_feature(context,feature):\n\tpass\n\n")
        text.writelines("def before_scenario(context,scenario):\n\tpass\n\n")
        text.writelines("def before_step(context,step):\n\tpass\n\n")
        text.writelines("def after_step(context,step):\n\tpass\n\n")
        text.writelines("def after_scenario(context,scenario):\n\tpass\n\n")
        text.writelines("def after_feature(context,feature):\n\tpass\n\n")
        text.writelines("def after_all(context):\n\tpass\n\n")
        text.close()
                
        text=open("features/behave.ini","w")
        text.writelines("[behave]\njunit=True\njunit_directory=./reports\nformat=json.pretty\noutfiles =./reports/test.json\nstdout_capture=True\nlog_capture=True\n")
        text.close
        
        text=open("steps/__init__.py","w")
        text.close()
        
        text=open("steps/models/__init__.py","w")
        text.close()
        
        text=open("steps/unit_test/__init__.py","w")
        text.close()
        
        text=open("lib/requerimento","w")
        text.writelines("Pyautomators")
        text.close()
        bank=sqlite3.connect("dados/bank.db")
        bank.close()    
     
    @staticmethod
    def criar_medotos(diretorio_features:str):
        
        '''lista para metodos armezenar'''
        lista_de_features=[]
        dicionario_de_steps=[]
        lista_implement=[]
        lista_metodo=[]
        
        '''ir para o diretorio'''
        os.chdir(diretorio_features)
        path=os.getcwd()
        path=str(path).replace("\\", "/")
        os.chdir("features")
        
        """ Lista de features na pasta"""
        pasta=os.listdir()
        for lista in pasta:
            valor=re.search(".feature",str(lista))
            if(valor!=None):
                lista_de_features.append(lista)

        """ Iterador de features"""
        for lin in lista_de_features:
            """ Iterador de Steps"""
            step=open(lin,"r+")
            valor=step.readlines()
            """ Iterador de linhas"""
            for valo in valor:
                """ Lista de valores para pesquisar padrao"""
                list=["Given","When","Then","And","But"]
                
                """ Iterador de valores de pesquisa"""
                for l in list:
                    valor=re.search(l,valo)
                    """ Tratamento se o valor for encontrado"""
                    if(valor!=  None):
                        
                        
                        listassteps=str(l).replace("Given","given").replace("When","when").replace("Then","then").replace("And","{}".format("and")).replace("\n", "").replace("But","{}".format("but"))
                        valorreal=str(valo).replace("\t","").replace("\n", "").replace("Given","").replace("When","").replace("Then","").replace("And","").replace("But","").replace("<","{").replace(">","}")
                        
                        
                        st=valorreal
                        string=st
                        
                        lista=[]
                        lista_de_parametros=[]
                        for s in range(len(string)):
                            
                            n=string[s].find("{")
                            m=string[s].find("}")
                            if(n!= -1 or m!= -1):
                                lista.append(s)
                        
                        entrada=numpy.arange(0,len(lista),2)
                        saidas=numpy.arange(1,len(lista),2)
                        
                        ran=len(entrada)
                        for r in range(ran):
                            
                            lista_de_parametros.append(str("").join((string[lista[entrada[r]]+1:lista[saidas[r]]])))
                        dicionario_de_steps.append([listassteps,valorreal[3:],lista_de_parametros,lin])
                        
         
        """ Gerar metodos"""
        ultimo_step=None
        parametro=0
        
    
        print(dicionario_de_steps)
        for step in dicionario_de_steps:
            context=""
            if(len(step[2])>0):
                contexto=[]
                for n in step[2]:
                    contexto.append(n)
                    
                
                context=str(",").join(contexto)
                context=","+context
            if(step[0]=="and"):
                step[0]=ultimo_step
            if(step[0]=="but"):
                step[0]=ultimo_step
            
            value="@{}('{}')\ndef step_implement(context{}):\n\tpass".format(step[0],step[1],context)
            lista_metodo.append(value)
            ultimo_step=step[0]
            parametro+=1
        ''' Gerar arquivo'''
        
        os.chdir(path+"/steps")
        steps=os.listdir() 
        for step in steps:
            pass
         
        """ Lista de implementacao"""
        implemento=[]
        for lista in lista_de_features:
            implemento.append(str("steps_"+lista).replace(".feature", ".py"))
        print(lista_de_features)
        for valor in implemento:
            print(valor)
            for step in steps:
                print(step)
                if(step==valor and step !=None):
                    list(steps).remove(step)
                    implemento.remove(valor)
        print(implemento)
        for implement in implemento:
            text=open(implement,'w')
            text.close()
        print(os.listdir())
        text=open(".py","r")
        a=text.readlines()
        
        
        for ls in dicionario_de_steps:
            n=ls[1]
            l=str(a).find(n)
            
            if(l>0):
                
                j=dicionario_de_steps.index(ls)
                
                lista_metodo[j]=str(None)
                
        
        text.close()
        text=open("steps_implement.py","a")
        
        
        for ls in lista_metodo:
            text.seek(0,2)
            if(ls!="None"):
                text.writelines(str(ls)+"\n\n\n")
        text.close()  