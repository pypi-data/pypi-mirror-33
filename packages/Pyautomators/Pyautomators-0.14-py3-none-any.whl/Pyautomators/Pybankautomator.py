'''
@author: KaueBonfim
'''
import MySQLdb
import cx_Oracle
import sqlite3
import sqlalchemy
from pandas.io import sql
from pymongo import MongoClient

class Relacional():
    
    def __init__(self,Servidor,user=None,senha=None,banco=None,endereco=None,porta=None):
        if (Servidor=="MySQL"):
            self.__bank=MySQLdb.connect(user=user,passwd=senha,db=banco,host=endereco,port=porta,autocommit=True)
            
        elif (Servidor=="Oracle"):
            self.__bank=cx_Oracle.connect('{}/{}@{}{}'.format(user,senha,endereco,porta))
            
        elif(Servidor=="SQLite"):
            self.__bank=sqlite3.connect(banco)
        
        self.cursor=self.__bank.cursor()
        
    def buscar_tudo(self,query:str):
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def buscar_um(self,query:str):
        self.cursor.execute(query)
        return self.cursor.fetchone()
    
        
    def inserir_lista(self,sql:str,valores:list):
        self.cursor.executemany(sql,valores)
        self.__bank.commit()
    
    def inserir(self,sql:str,valores:tuple):
        self.cursor.execute(sql,valores)
        self.__bank.commit()
    
    def deletar(self,sql:str,valores:tuple):
        self.cursor.execute(sql,valores)
        self.__bank.commit()
    
    def atualizar(self,sql:str,valores:tuple):
        self.cursor.execute(sql,valores)
        self.__bank.commit()
        
    def fechar_conexao(self):
        self.cursor.close()
        self.__bank.close()
        
    
    
class Alquimista():
    def __init__(self,url):       
        self.__engine=sqlalchemy.create_engine(url)
        
    def buscar(self,query,params=None):
        return sql.read_sql_query(sql=query, con=self.__engine, params=params)
    
    def DF_para_sql(self,DF,name):
        DF.to_sql(name,self.__engine)
    
    def inserir_tabela(self,sql,params):
        sql.execute(sql, con=self.__engine, params=params)
        
    def excluir_tabela(self,sql,params):
        sql.execute(sql, con=self.__engine, params=params)
    
    def atualizar_tabela(self,sql,params):
        sql.execute(sql, con=self.__engine, params=params)
        
class Nao_Relacional():
    def __init__(self,Servidor,banco=None,endereco=None,porta=None):       
        if(Servidor=='Mongo'):
            self.__con=MongoClient(endereco,porta)
            self.__bank=self.__con[banco]
            
    def buscar_um(self,params):
        return self.__bank.find_one(params)
    
    def buscar_tudo(self,params):
        return self.__bank.find(params)
    
    def atualizar(self,anterior,atual):
        self.__bank.update_one(anterior,atual)
        
    def inserir(self,params):
        self.__bank.insert_one(params)
        
    def inserir_lista(self,params):
        self.__bank.insert_many(params)
        
    def deletar_primeiro(self,params):
        self.__bank.delet_one(params)
        
    def deletar_tudo(self,params):
        self.__bank.delete_many(params)