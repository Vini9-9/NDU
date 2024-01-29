import pandas as pd
from flask import jsonify

class MyService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MyService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.df_games = self.load_csv('games')
        self.confrontation = self.generate_direct_confrontations(self.df_games)

    @staticmethod
    def load_csv(filename):
        """
        Carrega um arquivo CSV a partir do diretório 'files/'.

        :param filename: Nome do arquivo CSV (sem extensão) a ser carregado.
        :return: Um DataFrame do pandas contendo os dados do arquivo CSV.
        :raise FileNotFoundError: Se o arquivo de dados não for encontrado.
        """
        try:
            return pd.read_csv('files/' + filename + '.csv')
        except FileNotFoundError:
            return jsonify({'error': str("O arquivo de dados não foi encontrado.")}), 404

    def generate_direct_confrontations(cls, df_games):
        confrontos_diretos = {}

        # Iterar sobre os jogos e registrar os resultados dos confrontos diretos
        for _, jogo in df_games.iterrows():
            equipe_mandante = jogo['EQUIPE Mandante']
            equipe_visitante = jogo['EQUIPE Visitante']
            placar_mandante = jogo['GOLS_MANDANTE']
            placar_visitante = jogo['GOLS_VISITANTE']

            resultado = ''

            if placar_mandante > placar_visitante:
                resultado = equipe_mandante
            elif placar_mandante < placar_visitante:
                resultado = equipe_visitante
            else:
                resultado = 'E'

            # Registrar o resultado no dicionário
            confrontos_diretos.setdefault(equipe_mandante, {}).setdefault(equipe_visitante, resultado)
            confrontos_diretos.setdefault(equipe_visitante, {}).setdefault(equipe_mandante, resultado)

        return confrontos_diretos

    @property
    def df_games(self):
        return self._df_games

    @df_games.setter
    def df_games(self, novo_df_games):
        self._df_games = novo_df_games
        self._confrontation = self.generate_direct_confrontations(novo_df_games)

    @property
    def confrontation(self):
        return self._confrontation

    @confrontation.setter
    def confrontation(self, new_confrontation):
        self._confrontation = new_confrontation

    def get_df_games(self):
        return self.df_games
    
    def get_simulator_df_games(self):
        return self.load_csv('simulator/games')

    def get_confrontation(self):
        return self._confrontation

    def list_game_by_team(cls, team_surname):
        df_games = cls.get_df_games()
        condition_home = df_games['EQUIPE Mandante'].str.contains(team_surname)
        condition_away = df_games['EQUIPE Visitante'].str.contains(team_surname)
        games_by_team = df_games[condition_home | condition_away]
        return games_by_team

    def list_clashes(cls, teamOne, teamTwo):
        df_games = cls.get_df_games()
        # Filtrar os jogos onde a equipe é a mandante ou visitante
        condition_home = df_games['EQUIPE Mandante'].str.contains(teamOne)
        condition_away = df_games['EQUIPE Visitante'].str.contains(teamOne)

        # Combinar as condições usando o operador lógico OR (|)
        games_teamOne = df_games[condition_home | condition_away]

        # Filtrar os jogos onde a outra equipe é a visitante
        games_between_home = games_teamOne[games_teamOne['EQUIPE Mandante'].str.contains(teamTwo)]
        if games_between_home.empty == False:
            return games_between_home
        else:
            return games_teamOne[games_teamOne['EQUIPE Visitante'].str.contains(teamTwo)]

    def create_csv(cls, df, path, filename):
        df.to_csv(path + '/' + filename + '.csv', index=False)

    def tiebreaker_update_ranking(df_group):
        return df_group.sort_values(by=['Pontos', 'Saldo', 'Gols Pró'], ascending=[False, False, False])

    def direct_confrontation_update_ranking(df_group, teams_same_points, result_confront):
        team_ahead = result_confront
        teams_same_points.remove(team_ahead)
        # Nome da atlética que você deseja trocar
        team_behind = teams_same_points[0]

        # Encontrar a posição da atlética no DataFrame
        position_ahead = df_group.index[df_group['Atléticas'] == team_ahead].tolist()[0]
        position_behind = df_group.index[df_group['Atléticas'] == team_behind].tolist()[0]
        # Trocar os valores entre as linhas diretamente
        df_group.loc[position_ahead], df_group.loc[position_behind] = df_group.loc[position_behind].copy(), df_group.loc[position_ahead].copy()

        return df_group.sort_values(by='Pontos', ascending=False)

    def update_ranking(group, df_group, df_confrontos_diretos):
        row_equals_points = df_group[df_group.duplicated(subset='Pontos', keep=False)]

        # Obter apenas os nomes das atléticas
        teams_same_points = row_equals_points['Atléticas'].tolist()
        
        if len(teams_same_points) == 2:
            team_one = teams_same_points[0]
            team_two = teams_same_points[1]
            result_confront = df_confrontos_diretos.loc[team_one, team_two]

            if result_confront != 'E':
                return MyService.direct_confrontation_update_ranking(df_group, teams_same_points, result_confront)
        
        return MyService.tiebreaker_update_ranking(df_group)

    def concat_df_games(cls, new_game_data):
        new_df_games = pd.concat([cls.df_games, pd.DataFrame([new_game_data])], ignore_index=True)
        new_df_games.reset_index(drop=True)
        my_service.create_csv(new_df_games, 'files/simulator', 'games')

    def get_df_games_group(cls, group):
        df_games = cls.get_df_games()
        game_filter = df_games['GRUPO'] == group.upper()
        return df_games[game_filter]

    def get_simulator_df_ranking_group(cls, group):
        df = cls.load_csv('simulator/ranking_' + group.upper())
        return df

    def get_df_ranking_group(cls, group):
        return cls.load_csv('group/ranking_' + group.upper())

    def confrontos_to_df(cls, confrontos_diretos):
        # Criar um DataFrame a partir dos resultados dos confrontos diretos
        df_confrontos_diretos = pd.DataFrame(confrontos_diretos).T.fillna('').sort_index()
        df_confrontos_diretos.index.name = 'Equipes'
        return df_confrontos_diretos

    def update_direct_confrontation(cls, winner_team, loser_team, draw=False):
        confrontos_diretos = cls.confrontation  # Obtenha o dicionário atual
        if draw:
            resultado = 'E'
        else:
            resultado = winner_team

        # Registrar o resultado no dicionário
        confrontos_diretos.setdefault(winner_team, {}).setdefault(loser_team, resultado)
        confrontos_diretos.setdefault(loser_team, {}).setdefault(winner_team, resultado)
        # Atualizar a propriedade confrontation com o novo dicionário
        cls.confrontation = confrontos_diretos

    def simulate_game(cls, data_json):
        home_team = data_json['home_team']
        away_team = data_json['away_team']

        if my_service.list_clashes(home_team, away_team).empty == False:
            # TODO Return com info
            print("Não posso substituir um jogo que já existe")
        else:
            group     = data_json['group']
            home_goal = data_json['home_goal']
            away_goal = data_json['away_goal']
            
            game = {
                'GRUPO': group,
                'EQUIPE Mandante': home_team,
                'GOLS_MANDANTE': home_goal,
                'EQUIPE Visitante': away_team,
                'GOLS_VISITANTE': away_goal,
                'PLACAR': str(home_goal) + 'x' + str(away_goal),
                'SIMULADOR': True
            }

            # Definir df por grupo
            df_group = my_service.get_df_ranking_group(group)

            condition_home = df_group['Atléticas'] == home_team
            condition_away = df_group['Atléticas'] == away_team

        # Atualizar o número de jogos
            df_group.loc[condition_home, 'Jogos'] += 1
            df_group.loc[condition_away, 'Jogos'] += 1

        # Atualizar os gols
            df_group.loc[condition_home, 'Gols Pró'] += home_goal
            df_group.loc[condition_home, 'Gols Contra'] += away_goal

            df_group.loc[condition_away, 'Gols Pró'] += away_goal
            df_group.loc[condition_away, 'Gols Contra'] += home_goal

            df_group.loc[condition_home, 'Saldo'] += home_goal - away_goal
            df_group.loc[condition_away, 'Saldo'] += away_goal - home_goal

        # Atualizar os pontos
            if home_goal == away_goal:
                df_group.loc[condition_home, 'Pontos'] += 1
                df_group.loc[condition_away, 'Pontos'] += 1
                df_group.loc[condition_home, 'E'] += 1
                df_group.loc[condition_away, 'E'] += 1
                my_service.update_direct_confrontation(away_team, home_team, True)
            elif home_goal > away_goal:
                df_group.loc[condition_home, 'Pontos'] += 3
                df_group.loc[condition_home, 'V'] += 1
                df_group.loc[condition_away, 'D'] += 1
                my_service.update_direct_confrontation(home_team, away_team)
            else:
                df_group.loc[condition_away, 'Pontos'] += 3
                df_group.loc[condition_away, 'V'] += 1
                df_group.loc[condition_home, 'D'] += 1
                my_service.update_direct_confrontation(away_team, home_team)
            
            my_service.concat_df_games(game)
            
            df_new_group = MyService.update_ranking(group, df_group, my_service.confrontos_to_df(my_service.get_confrontation()))
            my_service.create_csv(df_new_group, 'files/simulator', 'ranking_' + group)
            return(game)

my_service = MyService()