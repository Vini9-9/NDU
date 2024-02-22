import pandas as pd
from flask import jsonify
from exception import *
import glob
import os
import re
from repository import FirebaseRepository

class MyService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MyService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        print("################# Iniciando Service #################")
        self.repository = FirebaseRepository()

    def get_confrontation(self, modality, series):
        return self.repository.get_confrontation(modality, series)

    def get_ranking(self, modality, series):
        return self.repository.get_ranking(modality, series)

    def get_games(self, modality, series):
        return self.repository.get_games(modality, series)
    
    def get_games_by_team(self, modality, series, team=None):
        return self.repository.get_games_by_team(modality, series, team)

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
            raise FileNotFoundErrorException()
        
    def generate_modality_series_data(self, modalidade, sexo, numero_series):
        series = ['A', 'B', 'C', 'D', 'E', 'F']

        modalidade_label = modalidade + ' ' + sexo
        
        dados = []
        for serie in series[:numero_series]:
            modalidade_value = modalidade[0] + sexo[0] + '/' + serie
            dados.append({
                "label": modalidade_label + " - Série " + serie,
                "modality": modalidade_label,
                "series": serie,
                "value": modalidade_value
            })
        
        return dados

    def generate_all_modalities(self):
        fm = self.generate_modality_series_data('Futsal', 'Masculino', 6)
        ff = self.generate_modality_series_data('Futsal', 'Feminino', 5)
        all_modalities = fm + ff
        return all_modalities
    
    def generate_all_rankings(self, modality, series, simulator=False):
        try:
            return self.get_ranking(modality, series)
        
        except FileNotFoundError:
            raise FileNotFoundErrorException()

    def generate_direct_confrontations(cls, df_games):
        confrontos_diretos = {}

        # Iterar sobre os jogos e registrar os resultados dos confrontos diretos
        for _, jogo in df_games.iterrows():
            equipe_mandante = jogo['Mandante']
            equipe_visitante = jogo['Visitante']
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

    def get_df_games_by_filepath(cls, filepath):
        return cls.load_csv(filepath + '/games')
    
    def get_simulator_df_games(self):
        return self.load_csv('simulator/games')

    # def get_confrontation(cls, filepath):
    #     df_games = cls.get_df_games_by_filepath(filepath)
    #     return cls.generate_direct_confrontations(df_games)

    def list_game_by_team(cls, team_surname, filepath):
        df_games = cls.get_df_games_by_filepath(filepath)
        condition_home = df_games['Mandante'].str.contains(team_surname)
        condition_away = df_games['Visitante'].str.contains(team_surname)
        games_by_team = df_games[condition_home | condition_away]
        return games_by_team

    def list_clashes(self, teamOne, teamTwo, modality, series):
        df_games = pd.DataFrame(self.get_games(modality, series))
        # Filtrar os jogos onde a equipe é a mandante ou visitante
        condition_home = df_games['Mandante'].str.contains(teamOne)
        condition_away = df_games['Visitante'].str.contains(teamOne)

        # Combinar as condições usando o operador lógico OR (|)
        games_teamOne = df_games[condition_home | condition_away]

        # Filtrar os jogos onde a outra equipe é a visitante
        games_between_home = games_teamOne[games_teamOne['Mandante'].str.contains(teamTwo)]
        if games_between_home.empty == False:
            return games_between_home
        else:
            return games_teamOne[games_teamOne['Visitante'].str.contains(teamTwo)]

    def create_csv(cls, df, path, filename):
        df.to_csv(path + '/' + filename + '.csv', index=False)

    def tiebreaker_update_ranking(df_group):
        return df_group.sort_values(by=['Pontos', 'Saldo', 'Gols_Pro'], ascending=[False, False, False])

    def direct_confrontation_update_ranking(df_group, teams_same_points, result_confront):
        team_ahead = result_confront
        teams_same_points.remove(team_ahead)
        # Nome da atlética que você deseja trocar
        team_behind = teams_same_points[0]

        # Encontrar a posição da atlética no DataFrame
        position_ahead = df_group.index[df_group['Time'] == team_ahead].tolist()[0]
        position_behind = df_group.index[df_group['Time'] == team_behind].tolist()[0]
        # Trocar os valores entre as linhas diretamente
        df_group.loc[position_ahead], df_group.loc[position_behind] = df_group.loc[position_behind].copy(), df_group.loc[position_ahead].copy()

        return df_group.sort_values(by='Pontos', ascending=False)

    def update_ranking(group, df_group, df_confrontos_diretos):
        row_equals_points = df_group[df_group.duplicated(subset='Pontos', keep=False)]

        # Obter apenas os nomes dos Times
        teams_same_points = row_equals_points['Time'].tolist()
        
        if len(teams_same_points) == 2:
            team_one = teams_same_points[0]
            team_two = teams_same_points[1]
            result_confront = df_confrontos_diretos.loc[team_one, team_two]

            if result_confront != 'E' and result_confront != '':
                return MyService.direct_confrontation_update_ranking(df_group, teams_same_points, result_confront)
        
        return MyService.tiebreaker_update_ranking(df_group)

    def concat_df_games(cls, new_game_data, filepath):
        df_games = cls.get_df_games_by_filepath(filepath)
        new_df_games = pd.concat([df_games, pd.DataFrame([new_game_data])], ignore_index=True)
        new_df_games.reset_index(drop=True)
        # my_service.create_csv(new_df_games, 'files/simulator', 'games')

    def get_df_games_group(cls, group):
        df_games = cls.get_df_games()
        game_filter = df_games['GRUPO'] == group.upper()
        return df_games[game_filter]

    def get_simulator_df_ranking_group(cls, group):
        df = cls.load_csv('simulator/ranking_' + group.upper())
        return df
    
    def get_simulator_df_ranking(cls):
        df = cls.load_csv('simulator/ranking')
        return df

    def get_df_ranking_group(self, group, modality, series):
        return self.repository.get_ranking_by_group(modality, series, group)

    def confrontos_to_df(cls, confrontos_diretos):
        # Criar um DataFrame a partir dos resultados dos confrontos diretos
        df_confrontos_diretos = pd.DataFrame(confrontos_diretos).T.fillna('').sort_index()
        df_confrontos_diretos.index.name = 'Equipes'
        return df_confrontos_diretos

    def update_direct_confrontation(self, modality, series, winner_team, loser_team, draw=False):
        confrontos_diretos = self.get_confrontation(modality, series)  # Obtenha o dicionário atual
        if draw:
            resultado = 'E'
        else:
            resultado = winner_team

        # Registrar o resultado no dicionário
        confrontos_diretos.setdefault(winner_team, {}).setdefault(loser_team, resultado)
        confrontos_diretos.setdefault(loser_team, {}).setdefault(winner_team, resultado)
        # Atualizar a propriedade confrontation com o novo dicionário
        self.confrontation = confrontos_diretos

    def simulate_game(self, data_json, modality, series):
        home_team = data_json['home_team']
        away_team = data_json['away_team']

        if self.list_clashes(home_team, away_team, modality, series).empty == False:
            raise GameAlreadyExistsException()
        else:
            group     = data_json['group']
            home_goal = data_json['home_goal']
            away_goal = data_json['away_goal']
            
            game = {
                'GRUPO': group,
                'Mandante': home_team,
                'GOLS_MANDANTE': home_goal,
                'Visitante': away_team,
                'GOLS_VISITANTE': away_goal,
                'PLACAR': str(home_goal) + 'x' + str(away_goal),
                'SIMULADOR': True
            }

            # Definir df por grupo
            df_group = pd.DataFrame(self.get_df_ranking_group(group, modality, series))

            condition_home = df_group['Time'] == home_team
            condition_away = df_group['Time'] == away_team

        # Atualizar o número de jogos
            df_group.loc[condition_home, 'Jogos'] += 1
            df_group.loc[condition_away, 'Jogos'] += 1

        # Atualizar os gols
            df_group.loc[condition_home, 'Gols_Pro'] += home_goal
            df_group.loc[condition_home, 'Gols_Contra'] += away_goal

            df_group.loc[condition_away, 'Gols_Pro'] += away_goal
            df_group.loc[condition_away, 'Gols_Contra'] += home_goal

            df_group.loc[condition_home, 'Saldo'] += home_goal - away_goal
            df_group.loc[condition_away, 'Saldo'] += away_goal - home_goal

        # Atualizar os pontos
            if home_goal == away_goal:
                df_group.loc[condition_home, 'Pontos'] += 1
                df_group.loc[condition_away, 'Pontos'] += 1
                df_group.loc[condition_home, 'E'] += 1
                df_group.loc[condition_away, 'E'] += 1
                self.update_direct_confrontation(modality, series, away_team, home_team, True)
            elif home_goal > away_goal:
                df_group.loc[condition_home, 'Pontos'] += 3
                df_group.loc[condition_home, 'V'] += 1
                df_group.loc[condition_away, 'D'] += 1
                self.update_direct_confrontation(modality, series, home_team, away_team)
            else:
                df_group.loc[condition_away, 'Pontos'] += 3
                df_group.loc[condition_away, 'V'] += 1
                df_group.loc[condition_home, 'D'] += 1
                self.update_direct_confrontation(modality, series, away_team, home_team)
            
            self.concat_df_games(game, modality, series)
            
            df_new_group = MyService.update_ranking(group, df_group, self.confrontos_to_df(self.get_confrontation(filepath)))
            # self.create_csv(df_new_group, 'files/simulator', 'ranking_' + group)
            return(game)

# my_service = MyService()