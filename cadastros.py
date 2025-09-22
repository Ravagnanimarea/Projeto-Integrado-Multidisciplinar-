'''Aqui vamos importar a biblioteca de "hashlib" onde ela criara um id anonimo junto
importei "time" para cada id se tornar unico'''

import hashlib
import time

'''Definimos uma class "protocolo" onde criaremos metodos
e nele atribuiremos "nome" e "descrição" onde vão ser estabelcidos valores assim que criado o objeto.'''

class protocolo:
    def _init_ (self, nome, descrição):
        self.nome = nome
        self.descrição = descrição
        
#Função para definir como o objeto será mostrado e nós retorna uma string formatada.
    def _str_(self):
        return f"{self.nome}: {self.descrição}"
    
'''Definimos uma class "Paciente" onde criaremos metodos e nele atribuiremos
"id", "faixa_etaria" e "sexo" onde vão ser estabelcidos valores assim que criado o objeto.'''

class Paciente:
    def _init_(self, faixa_etaria, sexo):
        base = f"{faixa_etaria}{sexo}{time.time()}"
        #Geramos um ID unico com base na idade, sexo e tempo
        self.id = hashlib.sha256(base.encode()).hexdigest()[:8]
        self.faixa_etaria = faixa_etaria
        self.sexo = sexo

#Função para definir como o objeto será mostrado e nós retorna uma string formatada.   
    def _str_(self):
        return (f"ID: {self.id} | idade: {self.faixa_etaria} | "
                f"sexo: {self.sexo}")
    
#Função para o cadastrando protocolos na lista 
def cadastrar_protocolo(lista_protocolos):
    nome = input("Nome do protocolo: ")
    descrição = input("Descrição do protocolo: ")
    #Cria um novo protocolo e "append" adiciona um unico elemento ao final da lista.
    novo_protocolo = protocolo(nome, descrição)
    lista_protocolos.append(novo_protocolo)
    print("Protocolo cadastrado com sucesso!")

#Função para mostrar a lista de protocolos ativo.
def listar_protocolos(lista_protocolos):
    if not lista_protocolos:
        print("Nenhum protocolo cadastrado.")
    else:
        for protocolo in lista_protocolos:
            print(protocolo)
            
def cadastrar_paciente(lista_pacientes):
    faixa_etaria = input ("Faixa etária: ")
    sexo = input ("Sexo(M/F): ")
    novo_paciente = Paciente(faixa_etaria, sexo)
    lista_pacientes.append (novo_paciente)
    print(f"Paciente cadastrado com sucesso! ID anônimo: {novo_paciente.id}")
    
def listar_pacientes(lista_pacientes):
    if not lista_pacientes:
        print("Nenhum paciente cadastrado.")
    else:
        for p in lista_pacientes:
            print (p)
            
protocolos_clinicos = []
pacientes_clinicos = []
while True:
    print("\nMenu:")
    print("1. Cadastrar protocolo")
    print("2. Listar protocolos")
    print("3. Cadastrar paciente")
    print("4. Listar pacientes")
    print("5. Sair")
    
    opcao = input("Escolha uma opção: ")
    if opcao == '1':
        cadastrar_protocolo(protocolos_clinicos)
    elif opcao == '2':
        listar_protocolos(protocolos_clinicos)
    elif opcao == '3':
        cadastrar_paciente(pacientes_clinicos)
    elif opcao == '4':
        listar_pacientes(pacientes_clinicos)
    elif opcao == '5':
        break
    
    else:
        print("Opção inválida.")
