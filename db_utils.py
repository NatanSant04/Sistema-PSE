import os
import sqlite3
import io
import base64
import matplotlib.pyplot as plt
from datetime import date, timedelta
from modelos import Treino, Atleta, RegistroDiario, TIPOS_DE_TREINO

# Define o caminho do banco de dados (o arquivo será criado na pasta do projeto)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "dados_atletas.db")


# Funções Utilitárias de Data

def get_semana_atual():
    """Retorna as datas de início (Segunda) e fim (Domingo) da semana atual no formato ISO."""
    hoje = date.today()
    dia_da_semana = hoje.weekday()
    inicio_semana = hoje - timedelta(days=dia_da_semana)
    fim_semana = inicio_semana + timedelta(days=6)
    return inicio_semana.isoformat(), fim_semana.isoformat()


def get_numero_semana_atual():
    """Retorna em qual semana do ano estamos."""
    hoje = date.today()
    return hoje.isocalendar()[1]


# Funções de Conexão e Estrutura do DB

def get_db_connection():
    """Cria e retorna a conexão com o banco de dados."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome (row['nome'])
    return conn


def criar_tabela():
    """Cria as tabelas ATLETAS e REGISTRO_TREINO, se não existirem."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # TABELA DE ATLETAS (NOMES E IDS)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ATLETAS (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE)
    """)

    # TABELA DE REGISTRO DIÁRIO (DADOS ÚNICOS POR DIA: PESO, LESÃO, RECUPERAÇÃO)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registro_diario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            atleta_id INTEGER NOT NULL,
            data TEXT NOT NULL,
            peso_diario REAL,
            lesao TEXT,
            recuperacao INTEGER,

            UNIQUE (atleta_id, data),
            FOREIGN KEY (atleta_id) REFERENCES ATLETAS (id)
        )
            ''')

    # TABELA DE TREINOS (DADOS MÚLTIPLOS POR DIA)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS treinos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            registro_diario_id INTEGER NOT NULL,
            tipo_treino TEXT NOT NULL,
            tempo_minutos INTEGER,
            cansaco INTEGER,
            pse INTEGER,

            FOREIGN KEY (registro_diario_id) REFERENCES registro_diario (id)
        )
            ''')

    conn.commit()
    conn.close()
    print(f'Tabelas criadas com sucesso em: {DB_PATH}')


# Funções de CRUD

def adicionar_atleta(nome):
    """Adiciona um atleta se ele ainda não existir."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR IGNORE INTO ATLETAS (nome) VALUES (?)", (nome,))
        conn.commit()
    except sqlite3.IntegrityError as e:
        print(f"Erro ao adicionar atleta {nome}: {e}")
    finally:
        conn.close()


def listar_atletas_com_id():
    """Retorna uma lista de tuplas com o ID e o nome de todos os atletas."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM ATLETAS ORDER BY nome")
    atletas = cursor.fetchall()
    conn.close()
    # RETORNAR (ID, NOME) PARA USAR NO HTML
    return [(row['id'], row['nome']) for row in atletas]


def buscar_atleta_id_por_nome(nome):
    """Retorna o ID do atleta dado o seu nome."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM ATLETAS WHERE nome = ?", (nome,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado['id'] if resultado else None


# Função para buscar o NOME pelo ID (necessário para o processamento)
def buscar_atleta_nome_por_id(atleta_id):
    """BUSCA O NOME DO ATLETA PELO ID numérico."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Busca o nome onde o ID seja igual ao ID que o formulário enviou
    cursor.execute("SELECT nome FROM ATLETAS WHERE id = ?", (atleta_id,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado['nome'] if resultado else None


def salvar_dados_no_bd(atleta: Atleta, registro: RegistroDiario):
    """Salva os dados de um registro diário e seus treinos no banco de dados."""
    conn = get_db_connection()
    cursor = conn.cursor()


    # BUSCA O ID NUMÉRICO DO ATLETA
    atleta_id = buscar_atleta_id_por_nome(atleta.nome)
    if atleta_id is None:
        print(f"Erro: Atleta '{atleta.nome}' não encontrado no Banco de Dados.")
        return
    try:
        recuperacao_do_dia = registro.lista_de_treinos[0].recuperacao if registro.lista_de_treinos else None

        # INSERIR O REGISTRO DIÁRIO QUE NÃO TERÁ MULDANÇAS (PESO, LESÃO, RECULPERÇÃO)
        cursor.execute('''
                INSERT OR IGNORE INTO registro_diario (atleta_id, data, peso_diario, lesao, recuperacao)
                VALUES (?, ?, ?, ?, ?)
            ''', (
            atleta_id,
            registro.data,
            registro.peso,
            registro.lesao,
            recuperacao_do_dia
        ))
        conn.commit()

        #TER A ID DO REGISTRO DIARIO
        cursor.execute("SELECT id FROM registro_diario WHERE atleta_id = ? AND data = ?", (atleta_id, registro.data))
        registro_diario_id = cursor.fetchone()['id']

        #REGISTRO DE TREINOS
        for treino in registro.lista_de_treinos:
            # O PSE é calculado por treino: Tempo * Cansaço
            pse_treino = treino.tempo_minutos * treino.cansaco
            cursor.execute('''
                        INSERT INTO treinos (registro_diario_id, tipo_treino, tempo_minutos, cansaco, pse)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                registro_diario_id,
                treino.tipo_treino,
                treino.tempo_minutos,
                treino.cansaco,
                pse_treino
            ))

            conn.commit()
            print(f'Registro diário e {len(registro.lista_de_treinos)} treino(s) salvos com sucesso!')
    except Exception as e:
        print(f"Erro ao salvar dados no BD: {e}")
        conn.rollback()
    finally:
        conn.close()
        print(f'Salvo com sucesso no banco de dados para {atleta.nome}!')


# Funções de Gráfico e Relatório

def pegar_dados_semanais(nome_atleta):
    """Busca os valores de data e PSE total na semana atual."""
    inicio_semana, fim_semana = get_semana_atual()
    atleta_id = buscar_atleta_id_por_nome(nome_atleta)

    if atleta_id is None: return []

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            rd.data, 
            SUM(t.pse) AS pse_total_dia
        FROM registro_diario rd
        JOIN treinos t ON rd.id = t.registro_diario_id
        WHERE rd.atleta_id = ? 
          AND rd.data BETWEEN ? AND ?
        GROUP BY rd.data
        ORDER BY rd.data 
        """, (atleta_id, inicio_semana, fim_semana))

    dados = cursor.fetchall()
    conn.close()

    return [(row['data'], row['pse_total_dia']) for row in dados]


def gerar_grafico_pse_semanal(nome_atleta):
    """Gera um gráfico de barras do PSE semanal e o retorna como string Base64."""

    dados_semanais = pegar_dados_semanais(nome_atleta)

    if not dados_semanais:
        return None

    datas = [dado[0] for dado in dados_semanais]
    pse_valores = [dado[1] for dado in dados_semanais]

    # CRIA OS DIAS DA SEMANA (RÓTULOS X)
    dias_semana_map = {
        0: 'Seg', 1: 'Ter', 2: 'Qua', 3: 'Qui', 4: 'Sex', 5: 'Sáb', 6: 'Dom'
    }

    x_labels = []

    for data_str in datas:
        data_obj = date.fromisoformat(data_str)
        dia_da_semana = dias_semana_map.get(data_obj.weekday(), data_str)
        x_labels.append(dia_da_semana)

    # CRIAÇÃO DO GRAFICO NO MATPLOTLIB
    plt.figure(figsize=(8, 5))
    plt.bar(x_labels, pse_valores, color='#3498db')

    plt.xlabel("Dia da semana")
    plt.ylabel("PSE Total")
    plt.title(f"Carga de Treino Semanal (PSE) - {nome_atleta}")

    # ADICIONAR OS VALORES DO PSE ACIMA DE CADA BARRA
    for i, valor in enumerate(pse_valores):
        plt.text(x_labels[i], valor + 5, str(valor), ha='center')

    plt.tight_layout()

    # SALVAR O GRAFICO NA MEMÓRIA
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()

    # CODIFICAÇÃO PARA BASE64
    buffer.seek(0)
    grafico_base64 = base64.b64encode(buffer.read()).decode('utf-8')

    return grafico_base64