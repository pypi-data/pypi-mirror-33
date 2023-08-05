#*- coding: utf-8 -*-
'''
@author: KaueBonfim
'''
import os
from jenkins import Jenkins

import testlink


class Jenkis():
    def __init__(self):
        self.jenkins_server=None
        
    def conectar_jenkins(self,url,senha_user,nome_user):
        self.jenkins_server= Jenkins(url,nome_user, senha_user)
    
    def construir_no_jenkins(self,nome):
        self.jenkins_server.build_job(nome)
        
class Git():  
    @staticmethod  
    def iniciar_repo(diretorio=None,nome=None,email=None):
       
        if(diretorio!=None):
            os.chdir(diretorio)
        os.system("git init")
        if(nome!=None):
            os.system('git config --local user.name %s'% nome)
        if(email!=None):
            os.system('git config --local user.email "%s"'% email)
        
        
    @staticmethod
    def add_repo(arquivos="*"):
        for lista in arquivos:
            os.system("git add %s" % lista)
            
    @staticmethod
    def commit(menssagem):
        os.system('git commit -m "%s"'% menssagem)
        
    @staticmethod
    def enviar_github(url):
        os.system("git remote add origem %s"% url)
        os.system("git push -f origem master")
        
    @staticmethod    
    def proxy_git(endereco,porta,usuario,senha):
        os.system('git config --local http.proxy http://{}:{}@{}:{}.git'.format(usuario,senha,endereco,porta))
        os.system('git config --local https.proxy https://{}:{}@{}:{}.git'.format(usuario,senha,endereco,porta))
    
class TestLink():
    
    def __init__(self,url_test_link,chave_usuario):
        
        self.testlink = testlink.TestLinkHelper(url_test_link,chave_usuario).connect(testlink.TestlinkAPIClient)
        

    def contar_testes(self):
        return self.testlink.countProjects()
    
    def pegar_caso_teste_nome(self,nome):
        retorno=[]
        for n in nome:
            retorno.append(*self.testlink.getTestCaseIDByName(n))
        return retorno
    
    def pegarCasoTeste(self,id):
        return self.testlink.getTestCaseByVersion(id)
    
    
    def pegarProjetos(self):
        return self.testlink.getProjects()
    
    def contar_suites(self):
        return self.testlink.countTestSuites()
    