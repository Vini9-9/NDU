from flask import Flask, jsonify, request
from flasgger import Swagger
from service import MyService
import pandas as pd


app     = Flask(__name__)
swagger = Swagger(app)

class MyApp:

  def __init__(self):
        self.service = MyService()

# Cria uma instância da classe MyApp
my_app = MyApp()

@app.route('/api/games', methods=['GET'])
def get_games():
    """
    Obtém informações sobre os jogos.
    ---
    responses:
      200:
        description: Lista de jogos.
    """
    df_games = my_app.service.get_df_games()
    return jsonify(df_games.to_dict(orient='records'))

@app.route('/api/games/confrontation', methods=['GET'])
def get_confrontation():
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
    team1_name = request.args.get('team1', type=str)
    team2_name = request.args.get('team2', type=str)

    confrontation = my_app.service.get_confrontation()
    if team1_name and team2_name:
      return confrontation[team1_name][team2_name]

    return jsonify(confrontation)

@app.route('/api/games/clashes', methods=['GET'])
def get_clashes():
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
    # df_games  = load_csv('games')
    team1_name = request.args.get('team1', type=str)
    team2_name = request.args.get('team2', type=str)

    df_clashes = my_app.service.list_clashes(team1_name, team2_name)
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

    df_games_group = my_app.service.get_df_games_group(group)

    return jsonify(df_games_group.to_dict(orient='records'))

@app.route('/api/games/team/<team>', methods=['GET'])
def get_games_by_team(team):
    """
    Obtém informações sobre os jogos por time.
    ---
    responses:
      200:
        description: Lista de jogos.
    """
    df_games_team = my_app.service.list_game_by_team(team)

    return jsonify(df_games_team.to_dict(orient='records'))

@app.route('/api/ranking/<group>', methods=['GET'])
def get_ranking(group):
    """
    Obtém o ranking de um grupo específico.
    ---
    parameters:
      - name: group
        in: query
        type: string
        description: Grupo para o qual o ranking deve ser obtido.
    responses:
      200:
        description: Ranking do grupo especificado.
      404:
        description: Grupo não encontrado.
    """
    df_group = get_df_ranking_group(group)
    
    return jsonify(df_group.to_dict(orient='records'))

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
        # game_req = {
        #   'group': request.form.get('group', type=str) 
        # }
        data_json = request.get_json()
        print(data_json)
        # confrontos_diretos = request.form.get('confrontos_diretos', type=str)

        # Chamar a função simular_jogo
        game = simulate_game(data_json, my_app.confrontation)

        return jsonify(
          {'message': 'Simulação do jogo realizada com sucesso.'},
          {'game': game}
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True, port=5001)