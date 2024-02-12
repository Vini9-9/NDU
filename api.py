from flask import Flask, jsonify, request
from flask_cors import CORS
from flasgger import Swagger
from service import MyService
import pandas as pd
import glob
import os
import re


app     = Flask(__name__)
CORS(app)
swagger = Swagger(app)

class MyApp:

  def __init__(self):
        self.service = MyService()
        print("!!!!!!!!!!!!!!!!!!!!! Iniciando MyApp !!!!!!!!!!!!!!!!!!!!!")

  def generateFilepath(modality, series):
        return modality + '/' + series

# Cria uma instância da classe MyApp
my_app = MyApp()
myAppService = my_app.service
my_service = MyService()

@app.route('/api/games/<modality>/<series>/confrontation', methods=['GET'])
def get_confrontation(modality, series):
    """
    Obtém informações sobre os confrontos.
    ---
    parameters:
      - name: team1
        in: query
        type: string
        description: Nome do primeiro time.
        required: true
      - name: team2
        in: query
        type: string
        description: Nome do segundo time.
        required: true
    responses:
      200:
        description: Lista de confrontos ou lista do vencedor do confronto.
    """
    filepath = MyApp.generateFilepath(modality, series)
    team1_name = request.args.get('team1', type=str)
    team2_name = request.args.get('team2', type=str)

    confrontation = my_service.get_confrontation(filepath)
    if team1_name and team2_name:
      return confrontation[team1_name][team2_name]

    return jsonify(confrontation)

@app.route('/api/games/<modality>/<series>/clashes', methods=['GET'])
def get_clashes(modality, series):
    """
    Obtém informações de confronto entre dois times.
    ---
    parameters:
      - name: team1
        in: query
        type: string
        description: Nome do primeiro time.
        required: true
      - name: team2
        in: query
        type: string
        description: Nome do segundo time.
        required: true
    responses:
      200:
        description: Informações de confronto entre os dois times.
      404:
        description: Pelo menos um dos times não foi encontrado.
    """
    filepath = MyApp.generateFilepath(modality, series)
    team1_name = request.args.get('team1', type=str)
    team2_name = request.args.get('team2', type=str)

    df_clashes = myAppService.list_clashes(team1_name, team2_name, filepath)
    return jsonify(df_clashes.to_dict(orient='records'))

@app.route('/api/games/group/<group>', methods=['GET'])
def get_games_by_group(group):
    """
    Obtém informações sobre os jogos por grupo.
    ---
    responses:
      200:
        description: Lista de jogos.
    """
    df_games_group = myAppService.get_df_games_group(group)

    return jsonify(df_games_group.to_dict(orient='records'))

@app.route('/api/games/<modality>/<series>', methods=['GET'])
def get_games_by_team(modality, series):
    """
    Obtém informações sobre os jogos por time.
    ---
    responses:
      200:
        description: Lista de jogos.
    """
    team_query = request.args.get('team')
    
    filepath = MyApp.generateFilepath(modality, series)

    if team_query:
      df_games = myAppService.list_game_by_team(team_query, filepath)
    else:
      df_games = my_service.get_df_games_by_filepath(filepath)
    return jsonify(df_games.to_dict(orient='records'))

@app.route('/api/ranking/<modality>/<series>', methods=['GET'])
def get_all_rankings(modality, series):
    """
    Obtém os rankings de todos os grupos.
    ---
    parameters:
      - name: simulator
        in: query
        type: boolean
        description: Indica se é para obter o ranking do simulador.
      - name: modality
        in: path
        type: string
        description: A modalidade para a qual o ranking deve ser obtido.
      - name: series
        in: path
        type: string
        description: A série para a qual o ranking deve ser obtido.
    responses:
      200:
        description: Rankings de todos os grupos.
    """
    simulator = request.args.get('simulator', type=bool)
    group_query = request.args.get('group')
    filepath_group =  MyApp.generateFilepath(modality, series) + '/group/'
    
    if group_query:
      df_group = myAppService.get_df_ranking_group(group_query, filepath_group)
      return jsonify(df_group.to_dict(orient='records'))

    all_rankings = []
    filepath = './files/' + filepath_group

    # Expressão regular para extrair a letra após "ranking_"
    regex_expression = r"ranking_([A-Z]+)\.csv"

    # Obtém os rankings de todos os grupos
    for filename in os.listdir(filepath):
    # Verifica se é um arquivo (não é um diretório)
      if os.path.isfile(os.path.join(filepath, filename)):
        group = re.match(regex_expression, filename).group(1)
        print("Listando grupo " + group)
        ranking_entry = {
              'group': group,
              'ranking': []
          }

        if simulator:
            df_group = myAppService.get_simulator_df_ranking_group(group)
        else:
            df_group = myAppService.get_df_ranking_group(group, filepath_group)
        
        ranking_entry['ranking'] = df_group.to_dict(orient='records')
        all_rankings.append(ranking_entry)

    return jsonify(all_rankings)

@app.route('/api/games/simulate', methods=['POST'])
def post_simulate_game():
    """
    Simula o resultado de um jogo.
    ---
    parameters:
      - name: group
        in: formData
        type: string
        description: Grupo do jogo.
        required: true
      - name: home_team
        in: formData
        type: string
        description: Equipe mandante.
        required: true
      - name: home_goal
        in: formData
        type: int
        description: Gols da equipe mandante.
        required: true
      - name: away_team
        in: formData
        type: string
        description: Equipe visitante.
        required: true
      - name: away_goal
        in: formData
        type: int
        description: Gols da equipe visitante.
        required: true
      - name: confrontos_diretos
        in: formData
        type: string
        description: Informações sobre confrontos diretos.
        required: true
    responses:
      200:
        description: Simulação do jogo realizada com sucesso.
      400:
        description: Parâmetros inválidos.
    """
    try:
        # Obter parâmetros da solicitação
        data_json = request.get_json()

        # Chamar a função simular_jogo
        game = my_service.simulate_game(data_json)

        return jsonify(
          {'message': 'Simulação do jogo realizada com sucesso.'},
          {'game': game}
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True, port=5001)