# Importação de bibliotecas.
import json
import random
import hashlib
import time
from datetime import datetime

# Função global utilizada para salvar os dados dos clientes em JSON.
def salvar_dados(lista_dados, caminho_arquivo): # Função recebe a lista que desejamos salvar e o nome do arquivo.
    try:
        if not lista_dados: # Caso a lista de dados esteja vazia, é printado um aviso de que a lista está vazia e não ocorrerá salvamento.
            print("Aviso: A lista de dados está vazia. Nenhum arquivo será salvo.")
            return
        
        with open(caminho_arquivo, 'w', encoding='utf-8') as arquivo_json: # Aqui estamos criando o arquivo JSON com o nome passado ao chamar a função.
            json.dump(lista_dados, arquivo_json, indent=4, ensure_ascii=False) # inserindo os dados, com algumas formatações utilizando indent e ascii.
        print(f"Dados salvos em {caminho_arquivo}, com sucesso!")
    except Exception as e: # Prevenção de erro caso ocorra problemas ao não salvar os arquivos. 
        print(f"Erro ao salvar o arquivo: {e}")

# Função global utilizada para carregar os dados.
def carregar_dados(caminho_arquivo):
    try:
        with open(caminho_arquivo, 'r', encoding="utf-8") as arquivo_json: # Estamos abrindo o arquivo ao chamar a função.
            return json.load(arquivo_json)
    except FileNotFoundError:
        print(f"Aviso: Arquivo {caminho_arquivo} não encontrado. Iniciando com lista vazia.") # Caso o arquivo não seja encontrado esse aviso é printado. 
        return[]

# -----------------------------
# Carregamento inicial de dados
# -----------------------------

protocolos = carregar_dados("protocolos.json")  # Lista de protocolos cadastrados
pacientes = carregar_dados("pacientes.json")  # Lista de pacientes cadastrados
eventos = carregar_dados("eventos.json") # Lista de eventos adversos
lotes = carregar_dados("lotes.json") # Lista de lotes
estoque = carregar_dados("estoque.json") # Lista de itens em estoque
indicadores_data = carregar_dados("indicadores.json") # Lista de KPIs ambientais

#Classe Protocolo para definir os atributos que utilizaremos para cadastrar um protocolo.
class Protocolo:
    def __init__(self, nome, descricao, tipo_tratamento):
        self.nome = nome
        self.descricao = descricao
        self.tipo_tratamento = tipo_tratamento

class No:
    def __init__(self, paciente):
        self.paciente = paciente
        self.esquerda = None
        self.direita = None
        self.altura = 1 #Usado para calcular o equilibrio da árvore

# Classe Paciente para definir os atributos que serão utilizado para cadastrar um paciente.
class Paciente:
    def __init__(self, idade, sexo):
        self.idade = idade
        self.sexo = sexo
        # Gera ID anonimizados usando hash SHA-256 + timestamp
        s = f"{idade}{sexo}{time.time()}{random.randint(1, 1000)}"
        self.id = hashlib.sha256(s.encode()).hexdigest()[:8]  # 8 primeiros caracteres do hash

# Classe que implementa uma árvore AVL para armazenar pacientes por idade
class ArvorePacientes:
    def __init__(self):
        # Raiz inicial da árvore
        self.raiz = None

    # Inserir novo paciente na árvore
    def inserir_paciente(self, paciente):
        # Chama função recursiva que manipula nós e balanceia
        self.raiz = self._inserir(self.raiz, paciente)

    # Função recursiva para inserir e balancear
    def _inserir(self, raiz, paciente):
        # Se chegou em uma posição vazia, cria um novo nó com o paciente
        if raiz is None:
            return No(paciente)
        # Percorre para esquerda se a idade do paciente for menor que a do nó atual
        if paciente.idade < raiz.paciente.idade:
            raiz.esquerda = self._inserir(raiz.esquerda, paciente)
        else:
            # Caso contrário, percorre para a direita
            raiz.direita = self._inserir(raiz.direita, paciente)

        # Atualizar altura
        raiz.altura = 1 + max(self.get_altura(raiz.esquerda),
                            self.get_altura(raiz.direita))

        # Calcular o fator de equilíbrio
        balance = self.get_balance(raiz)

        # Rotacionar se estiver desbalanceado
        # Caso Esquerda-Esquerda
        if balance > 1 and paciente.idade < raiz.esquerda.paciente.idade:
            return self.rotacao_direita(raiz)

        # Caso Direita-Direita
        if balance < -1 and paciente.idade > raiz.direita.paciente.idade:
            return self.rotacao_esquerda(raiz)

        # Caso Esquerda-Direita
        if balance > 1 and paciente.idade > raiz.esquerda.paciente.idade:
            raiz.esquerda = self.rotacao_esquerda(raiz.esquerda)
            return self.rotacao_direita(raiz)

        # Caso Direita-Esquerda
        if balance < -1 and paciente.idade < raiz.direita.paciente.idade:
            raiz.direita = self.rotacao_direita(raiz.direita)
            return self.rotacao_esquerda(raiz)

        # Se já está balanceado, retorna a raiz atual
        return raiz
    
# -----------------------------
# Estratificação de risco
# # -----------------------------

    def estratificar_por_risco(self):
        """Estratificação de pacientes por risco - Complexidade: O(n)"""
        grupos = {"baixo": [], "medio": [], "alto": []}
        self._estratificar(self.raiz, grupos)
        return grupos

    def _estratificar(self, raiz, grupos):
        if raiz:
            self._estratificar(raiz.esquerda, grupos)
            if raiz.paciente.idade < 50:
                grupos["baixo"].append(raiz.paciente.id)
            elif raiz.paciente.idade < 65:
                grupos["medio"].append(raiz.paciente.id)
            else:
                grupos["alto"].append(raiz.paciente.id)
            self._estratificar(raiz.direita, grupos)
            
# -----------------------------
# Detecção de outliers
# -----------------------------
            
    def detectar_outliers(self, no=None, resultado=None):
        if resultado is None:
            resultado = []

        # Define a raiz apenas na primeira chamada
        if no is None:
            no = self.raiz
        if no is None:
            return resultado  # árvore vazia

        # 🚫 Condição de parada — evita recursão infinita
        if no is None:
            return resultado

        # Percorre subárvore esquerda
        if no.esquerda:
            self.detectar_outliers(no.esquerda, resultado)

        # Verifica se o paciente é um outlier (idade > 80)
        if no.paciente.idade > 80:
            resultado.append({
            "id": no.paciente.id,
            "idade": no.paciente.idade
        })

        # Percorre subárvore direita
        if no.direita:
            self.detectar_outliers(no.direita, resultado)

        return resultado

    # Retorna altura do nó
    def get_altura(self, no):
        if not no:
            return 0
        return no.altura

    # Retorna fator de equilíbrio
    def get_balance(self, no):
        if not no:
            return 0
        return self.get_altura(no.esquerda) - self.get_altura(no.direita)

    # Rotação à direita
    def rotacao_direita(self, y):
        # x é o filho esquerdo de y
        x = y.esquerda
        # T2 é a subárvore direita de x que será realocada
        T2 = x.direita

        # Executa rotação
        x.direita = y
        y.esquerda = T2

        # Atualiza alturas
        y.altura = 1 + max(self.get_altura(y.esquerda),
                        self.get_altura(y.direita))
        x.altura = 1 + max(self.get_altura(x.esquerda),
                        self.get_altura(x.direita))

        return x

    # Rotação à esquerda
    def rotacao_esquerda(self, x):
        y = x.direita
        T2 = y.esquerda

        # Executa rotação
        y.esquerda = x
        x.direita = T2

        # Atualiza alturas
        x.altura = 1 + max(self.get_altura(x.esquerda),
                        self.get_altura(x.direita))
        y.altura = 1 + max(self.get_altura(y.esquerda),
                        self.get_altura(y.direita))

        return y

    # Impressão em ordem (menor idade → maior idade)
    def imprimir(self):
        print("\n--- Pacientes cadastrados (em ordem de idade) ---")
        self._imprimir(self.raiz)

    # Função auxiliar recursiva para imprimir em ordem
    def _imprimir(self, raiz):
        if raiz:
            # Visita subárvore esquerda
            self._imprimir(raiz.esquerda)
            # Imprime dados do paciente no nó atual
            print(f"ID: {raiz.paciente.id} | Idade: {raiz.paciente.idade} | Sexo: {raiz.paciente.sexo}")
            # Visita subárvore direita
            self._imprimir(raiz.direita)

# -----------------------------
# Teste da arvore
# -----------------------------
if __name__ == "__main__":
    # Cria instância da árvore
    arvore = ArvorePacientes()
    # Cria alguns pacientes de exemplo
    p1 = Paciente(30, "F")
    p2 = Paciente(50, "M")
    p3 = Paciente(40, "F")

    # Insere os pacientes na árvore
    arvore.inserir_paciente(p1)
    arvore.inserir_paciente(p2)
    arvore.inserir_paciente(p3)
    
    grupos= arvore.estratificar_por_risco()
    print(grupos)
    
    outliers = arvore.detectar_outliers()
    print(outliers)
    
    # Imprime a árvore em ordem
    arvore.imprimir()
    
# Função utilizada para cadastrar protocolo.
def cadastrar_protocolo():
    nome = input("Nome do protocolo: ")
    descricao = input("Descricao: ")
    tipo = input("Tipo de tratamento: ")
    protocolos.append(Protocolo(nome, descricao, tipo).__dict__) # Estamos chamando a calsse protocolo passando os dados do input, transformando os dados em dicionário para posteriormente salvarmos em JSON e inserindo em protocolos.
    print(f"Protocolo '{nome}' cadastrado!")

# Função utilizada para cadastrar paciente.
def cadastrar_paciente():
    idade = int(input("Idade (Somente números): "))
    sexo = input("Sexo (M/F): ")
    p = Paciente(idade, sexo) # Estamos atribuindo para p a classse Paciente, passando os dados do input.
    pacientes.append(p.__dict__) # Estamos transformando p em dicionário e inserindo na lista de paciente. A transofrmação em dicionário é para salvar em JSON posteriormente. 
    print(f"Paciente cadastrado! ID anonimizado: {p.id}")

# Função utilizada para randomizar o grupo, fazendo com que ele caia no grupo de tratamento ou placebo.
def randomizar_grupo(paciente_id):
    grupo = random.choice(["Tratamento", "Placebo"])
    paciente_id['grupo'] = grupo
    return grupo

# Função utilizada para eventos adversos.
def registrar_evento():
    paciente_id = input("ID do paciente: ")
    descricao = input("Descrição do evento adverso: ")
    eventos.append({"paciente": paciente_id, "descricao": descricao})
    print("Evento registrado!")

# Função utilizada para registrar lote.
def registrar_lote():
    numero = input("Número do lote: ")
    lotes.append({"numero": numero})
    print("Lote registrado!")

# Função utilizada para atualizar e controlar estoque de produto. 
def controlar_estoque():
    item = input("Item: ")
    qtd = int(input("Quantidade: "))
    estoque.append({"item": item, "quantidade": qtd})
    print("Estoque atualizado!")

# Função utilizada para gerar relatório dos dados.
def gerar_relatorio():
    relatorio = {
        "protocolos": protocolos,
        "pacientes": pacientes,
        "eventos": eventos,
        "lotes": lotes,
        "estoque": estoque,
        "gerado_em": datetime.now().isoformat() # Ao gerar o relatório pegamos o horário atual em que o relatório foi gerado.
    }
    print("=== Relatório Regulatório ===")
    print(json.dumps(relatorio, indent=2, ensure_ascii=False))

# Classe de indicadores utilizada para registrar KPIs ambientais.
class Indicadores:
    def __init__(self):
        self.energia = 0
        self.solventes_recuperados = 0

    def registrar(self, energia, solventes):
        self.energia += energia
        self.solventes_recuperados += solventes

    def mostrar(self):
        print("KPIs Ambientais:", json.dumps(self.__dict__, indent=2))

    def to_dict(self): # Transformação em dicionário para salvar em JSON posteriormente.
        return self.__dict__

# Classe utilizada para definir o status do modulo educacional, definido se está concluído ou não. 
class ModuloEducacional:
    def __init__(self, nome):
        self.nome = nome
        self.concluido = False

    def concluir(self):
        self.concluido = True
        print(f"Módulo '{self.nome}' concluído!")
    
    def to_dict(self): # Transformação em dicionário para salvar em JSON posteriormente.
        return self.__dict__

indicadores = Indicadores()
modulo_ambiental = ModuloEducacional("Boas práticas ambientais")

# Função menu que continua rodando até que seja pausado com break ao usuário escolher a opção 13. 
def menu():
    while True:
        print("\nMenu:")
        print("1. Cadastrar protocolo")
        print("2. Cadastrar paciente")
        print("3. Registrar evento adverso")
        print("4. Randomizar grupo de paciente")
        print("5. Registrar lote")
        print("6. Atualizar estoque")
        print("7. Gerar relatório regulatório")
        print("8. Registrar KPIs ambientais")
        print("9. Concluir módulo educacional")
        print("10. Estratificar risco de pacientes")
        print("11. Detectar outliers")
        print("12. Salvar dados")
        print("13. Sair")
        opcao = input("Escolha uma opção: ")

        # Estamos realizando if para realizar ações conforme a opção selecionada pelo usiário.
        if opcao == '1':
            cadastrar_protocolo()
        elif opcao == '2':
            cadastrar_paciente()
        elif opcao == '3':
            registrar_evento()
        elif opcao == '4':
            pid = input("ID do paciente: ")
            paciente_encontrado = next((p for p in pacientes if p['id'] == pid), None) # Aqui estamos iterando pela lista de pacientes para pegar o primeiro paciente com o id igual ao passado no input.
            if paciente_encontrado: # Aqui é uma prevenção de erro, caso o paciente seja encontrado, iremos executar a funçao randomizar_grupo.
                grupo = randomizar_grupo(paciente_encontrado)
                print(f"Paciente {pid} alocado no grupo {grupo}")
            else:
                print("Paciente não encontrado, insira um ID válido.") # Caso o ID não seja de um paciente válido, irá aparecer um aviso de ID inválido.
        elif opcao == '5':
            registrar_lote()
        elif opcao == '6':
            controlar_estoque()
        elif opcao == '7':
            gerar_relatorio()
        elif opcao == '8':
            e = int(input("Energia consumida (Somente numeros):"))
            s = int(input("Solventes recuperados: "))
            indicadores.registrar(e, s)
            indicadores.mostrar()
        elif opcao == '9':
            modulo_ambiental.concluir()
        elif opcao == '10':
            print("Grupos de risco:", arvore.estratificar_por_risco())
        elif opcao == '11':
            outliers = arvore.detectar_outliers()
            if outliers:
                print("\nPacientes fora da curva (idade > 80):")
                for p in outliers:
                    print(f"ID: {p['id']}, Idade: {p['idade']}")
            else:
                print("\nNenhum paciente fora da curva encontrado.")
        elif opcao == '12': # Aqui qestamos chaamando a função global de salvamento para salvar todas as listas.
            print("\nSalvando todos os dados...")
            salvar_dados(protocolos, "protocolos.json")
            salvar_dados(pacientes, "pacientes.json")
            salvar_dados(eventos, "eventos.json")
            salvar_dados(lotes, "lotes.json")
            salvar_dados(estoque, "estoque.json")
            salvar_dados([indicadores.to_dict()], "indicadores.json")
            salvar_dados([modulo_ambiental.to_dict()], "modulo_ambiental.json")
        elif opcao == '13': # Ao selecionar a opção 13 o sistema para e o menu deixa de ser exibido.
            print("Saindo do programa.")
            break 
        else:
            print("Opção inválida.") # Prevençaõ de erro caso a opção digitada não esteja disponível.

if __name__ == "__main__":
    menu()


