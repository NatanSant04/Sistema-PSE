import datetime

TIPOS_DE_TREINO = ['Randori', 'Tecnico', 'Fisico', 'Outros']

class Treino: 
#ENTRADAS DETALHADAS PARA O PSE
	def __init__ (self, recuperacao, tipo_treino, tempo_minutos, cansaco): 
		self.recuperacao = recuperacao
		self.tipo_treino = tipo_treino
		self.tempo_minutos = tempo_minutos
		self.cansaco = cansaco
		
class RegistroDiario:
#ENTRADAS QUE SERAO DIARIAS
	def __init__ (self, data, peso, lesao):
		self.data = data
		self.peso = peso
		self.lesao = lesao
		self.lista_de_treinos = []

	def adicionar_treino(self, treino):
		self.lista_de_treinos.append(treino)



class Atleta: 
#REGISTRO DIARIO DE CADA ATLETA
	def __init__ (self, nome):
		self.nome = nome
		self.registro_diario = []
	
	def adicionar_registro_diario(self, registro):
		self.registro_diario.append(registro)

