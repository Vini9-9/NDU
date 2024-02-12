from flask import Flask, jsonify, request
from flask_cors import CORS
from flasgger import Swagger
from service import MyService
from exception import *
import pandas as pd



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
# myAppService = MyService()

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
      - name: modality
        in: path
        type: string
        description: A modalidade dos jogos.
      - name: series
        in: path
        type: string
        description: A série dos jogos.
    responses:
      200:
        description: Lista de confrontos ou lista do vencedor do confronto.
    """
    try:

      filepath = MyApp.generateFilepath(modality, series)
      team1_name = request.args.get('team1', type=str)
      team2_name = request.args.get('team2', type=str)

      confrontation = myAppService.get_confrontation(filepath)
      if team1_name and team2_name:
        return confrontation[team1_name][team2_name]

      return jsonify(confrontation)

    except Exception as e:
        return jsonify({'error': e.message}), e.errorCode

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
      - name: modality
        in: path
        type: string
        description: A modalidade dos jogos.
      - name: series
        in: path
        type: string
        description: A série dos jogos.
    responses:
      200:
        description: Informações de confronto entre os dois times.
      404:
        description: Pelo menos um dos times não foi encontrado.
    """
    try:

      filepath = MyApp.generateFilepath(modality, series)
      team1_name = request.args.get('team1', type=str)
      team2_name = request.args.get('team2', type=str)

      df_clashes = myAppService.list_clashes(team1_name, team2_name, filepath)
      return jsonify(df_clashes.to_dict(orient='records'))

    except Exception as e:
        return jsonify({'error': e.message}), e.errorCode

@app.route('/api/games/group/<group>', methods=['GET'])
def get_games_by_group(group):
    """
    Obtém informações sobre os jogos por grupo.
    ---
    responses:
      200:
        description: Lista de jogos.
    """
    try:
      df_games_group = myAppService.get_df_games_group(group)

      return jsonify(df_games_group.to_dict(orient='records'))

    except Exception as e:
        return jsonify({'error': e.message}), e.errorCode

@app.route('/api/games/<modality>/<series>', methods=['GET'])
def get_games(modality, series):
    """
    Obtém informações sobre os jogos por time.
    ---
    parameters:
    - name: modality
      in: path
      type: string
      description: A modalidade dos jogos.
    - name: series
      in: path
      type: string
      description: A série dos jogos.
    responses:
      200:
        description: Lista de jogos.
    """
    try:

      team_query = request.args.get('team')
      
      filepath = MyApp.generateFilepath(modality, series)

      if team_query:
        df_games = myAppService.list_game_by_team(team_query, filepath)
      else:
        df_games = myAppService.get_df_games_by_filepath(filepath)
      return jsonify(df_games.to_dict(orient='records'))

    except Exception as e:
        return jsonify({'error': e.message}), e.errorCode

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
    try:
      simulator = request.args.get('simulator', type=bool)
      group_query = request.args.get('group')
      filepath_group =  MyApp.generateFilepath(modality, series) + '/group/'

      if group_query:
        df_group = myAppService.get_df_ranking_group(group_query, filepath_group)
        return jsonify(df_group.to_dict(orient='records'))

      all_rankings = myAppService.generate_all_rankings(filepath_group)

      return jsonify(all_rankings)
      
    except Exception as e:
      return jsonify({'error': e.message}), e.errorCode
      
@app.route('/api/simulate/<modality>/<series>/games', methods=['POST'])
def post_simulate_game(modality, series):
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
    filepath_group =  MyApp.generateFilepath(modality, series)
    try:
        # Obter parâmetros da solicitação
        data_json = request.get_json()

        # Chamar a função simular_jogo
        game = myAppService.simulate_game(data_json, filepath_group)

        return jsonify(
          {'message': 'Simulação do jogo realizada com sucesso.'},
          {'game': game}
        )
    except Exception as e:
        return jsonify({'error': e.message}), e.errorCode


if __name__ == '__main__':
    app.run(debug=True, port=5001)