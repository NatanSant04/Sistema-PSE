Este projeto é uma aplicação web desenvolvida em Python e Flask para monitorar a carga de treinamento e o bem-estar de atletas de alto rendimento. O sistema permite a coleta diária de dados e gera análises visuais automáticas para a comissão técnica.

**Funcionalidades Atuais**
Registro Diário de Atletas: Coleta de Peso, Percepção Subjetiva de Esforço (PSE), Nível de Recuperação e Relatos de Lesão.

Painel de Análise Individual: Visualização de gráficos de linha e barras por atleta e por semana.

Relatório Geral da Equipe: Visão consolidada de todos os atletas em uma única tela, facilitando a identificação de riscos de overtraining ou lesões.

Análise de Wellness: Gráfico específico para monitorar a recuperação do atleta (Escala 1-10).

Monitoramento Biométrico: Acompanhamento da variação de peso e cálculo de média semanal automática.

**Tecnologias Utilizadas**
Backend: Python 3.x com framework Flask.

Banco de Dados: SQLite para armazenamento local e persistente.

Visualização de Dados: Matplotlib para geração dinâmica de gráficos em formato Base64.

Frontend: HTML5 e CSS3 com design Mobile-First (totalmente responsivo para celulares).

**Estrutura de Monitoramento**
O sistema foca na "Tríade de Performance":

Carga Interna (PSE): O quanto o treino foi intenso para o atleta.

Prontidão (Recuperação): O estado físico e mental antes/após a atividade.

Saúde (Peso e Lesão): Monitoramento de categorias de peso e alertas de dores ou lesões.

**Como Rodar o Projeto**
1. Clone o repositório;
2. Instale as dependências;
3. Execute a aplicação;
4. Acesse no navegador.

**Próximos Passos (Roadmap)**
[ ] Implementação de sistema de autenticação (Login/Senha) para Comissão Técnica.

[ ] Exportação de relatórios em PDF.

[ ] Integração com Nuvem (Hospedagem em servidor público).
