from flask import Flask, render_template, request, redirect, url_for
from datetime import date
import db_utils
from modelos import Atleta, Treino, RegistroDiario, TIPOS_DE_TREINO

# CRIAR A APLICAÇÃO DO FLASK
app = Flask(__name__)


# --- Rota Principal (O Formulário de Entrada de Dados) ---

@app.route('/', methods=['GET', 'POST'])
def index():
    # Garante que as tabelas existam
    db_utils.criar_tabela()

    # BUSCAR NA LISTA DE ATLETAS
    atletas_disponiveis = db_utils.listar_atletas_com_id()

    if request.method == 'POST':  # SE OS DADOS FOREM ENVIADOS, PROCESSE-OS
        return processar_registro()

    # RENDERIZAÇÃO DA PAGINA DE FORMULARIO, EM CASO DE GET
    return render_template(
        'index.html',
        atletas=atletas_disponiveis,
        tipos_treino=TIPOS_DE_TREINO
    )


# ROTA DE PROCESSO DO FORMULARIO
def processar_registro():
    # 1. PEGAR OS DADOS COMO STRING
    atleta_id = request.form.get('atleta_id')
    nome_atleta = db_utils.buscar_atleta_nome_por_id(atleta_id)
    if nome_atleta is None:
        return "Erro 400: Atleta não encontrado.", 400

    peso_input = request.form.get('peso_dia')
    recuperacao_input = request.form.get('recuperacao_nivel')
    lesao = request.form.get('lesao_obs')

    tipo_treino = request.form.get('tipo_treino')
    tempo_minutos_input = request.form.get('tempo_minutos')
    cansaco_input = request.form.get('cansaco_nivel')

    # CHECAGEM DE OBRIGATORIEDADE
    if not (atleta_id and peso_input and recuperacao_input and tempo_minutos_input and cansaco_input):
        return "Erro 400: Por favor, preencha todos os campos obrigatórios.", 400

    # 2. CONVERSÃO E CHECAGEM DE FORMATO (DENTRO DO TRY)
    try:
        atleta_id=int(atleta_id)
        peso = float(peso_input)
        recuperacao = int(recuperacao_input)
        tempo_minutos = int(tempo_minutos_input)
        cansaco = int(cansaco_input)
    except ValueError:
        return "Erro 400: Formato inválido. Use apenas números inteiros ou decimais.", 400

    # 3. BARREIRA DE SEGURANÇA FINAL (Limites 1-10)
    if not (1 <= cansaco <= 10 and 1 <= recuperacao <= 10):
        return "Erro 400: Os níveis de Cansaço e Recuperação devem ser entre 1 e 10.", 400

    nome_atleta = db_utils.buscar_atleta_nome_por_id(atleta_id)
    if not nome_atleta:
        return "Erro: Atleta não encontrado.", 400

    # 4. CRIAÇÃO DOS OBJETOS PYTHON E SALVAMENTO NO BD
    atleta = Atleta(nome=nome_atleta)

    registro_hoje = RegistroDiario(
        data=date.today().isoformat(),
        peso=peso,
        lesao=lesao
    )

    treino = Treino(
        recuperacao=recuperacao,
        tipo_treino=tipo_treino,
        tempo_minutos=tempo_minutos,
        cansaco=cansaco
    )

    registro_hoje.adicionar_treino(treino)
    db_utils.salvar_dados_no_bd(atleta, registro_hoje)

    # 5. REDIRECIONAR PARA A PARGINA INICIAL
    return redirect(url_for('index'))


# ROTA PARA RELATORIO E GRAFICOS / CADASTRO
@app.route('/relatorios', methods=['GET', 'POST'])
def relatorios():
    atletas_disponiveis = db_utils.listar_atletas_com_id()
    grafico_base64 = None
    nome_atleta_selecionado = ""
    mensagem_cadastro = None

    # CADASTRO DE ATLETAS
    if request.method == 'POST':
        nome_novo_atleta = request.form.get('nome_novo_atleta')
        if nome_novo_atleta:
            db_utils.adicionar_atleta(nome_novo_atleta)
            mensagem_cadastro = f"Atleta '{nome_novo_atleta}' adicionado com sucesso! Selecione para gerar o relatório."
            # ATUALIZAR A LISTA
            atletas_disponiveis = db_utils.listar_atletas_com_id()

    # PEGANDO DADOS PARA O GRÁFICO
    atleta_nome_param = request.args.get('atleta_nome')
    numero_semana = db_utils.get_numero_semana_atual()

    if atleta_nome_param:
        nome_atleta_selecionado = atleta_nome_param
        grafico_base64 = db_utils.gerar_grafico_pse_semanal(nome_atleta_selecionado)

    # RETORNO FINAL: RENDERIZAÇÃO DA PÁGINA DE RELATÓRIOS
    return render_template(
        'relatorios.html',
        atletas=atletas_disponiveis,
        nome_selecionado=nome_atleta_selecionado,
        grafico=grafico_base64,
        numero_semana=numero_semana,
        mensagem_cadastro=mensagem_cadastro  # Passa a mensagem de sucesso
    )


# INICIALIZAÇÃO DO FLASK
if __name__ == '__main__':
    # GARANTIA QUE AS TABELAS ESTEJAM CRIADAS
    db_utils.criar_tabela()

    print('O Flask esta rodando')
    app.run(debug=True, host='0.0.0.0')
