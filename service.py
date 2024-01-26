import pandas as pd

class MyService:
    def __init__(self):
        self.df_games = self.load_csv('games')
        # self.confrontation = self.generate_direct_confrontations(self.df_games)

    @staticmethod
    def load_csv(filename):
        """
        Carrega um arquivo CSV a partir do diretório 'files/'.

        :param filename: Nome do arquivo CSV (sem extensão) a ser carregado.
        :return: Um DataFrame do pandas contendo os dados do arquivo CSV.
        :raise FileNotFoundError: Se o arquivo de dados não for encontrado.
        """
        try:
            df = pd.read_csv('files/' + filename + '.csv')
            return df
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

    def get_df_games(self):
        return self.df_games

    def get_confrontation(self):
        return self._confrontation
    

    def list_game_by_team(team_surname):
        df_games = self.get_df_games()
        condition_home = df_games['EQUIPE Mandante'].str.contains(team_surname)
        condition_away = df_games['EQUIPE Visitante'].str.contains(team_surname)
        games_by_team = df_games[condition_home | condition_away]
        return games_by_team

    def list_clashes(teamOne, teamTwo):
        df_games = self.get_df_games()
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

    def update_ranking(group, df_confrontos_diretos):
        if group == 'A':
            df_group = df_groupA
        elif group == 'B':
            df_group = df_groupB

        linhas_pontos_iguais = df_group[df_group.duplicated(subset='Pontos', keep=False)]

        # Obter apenas os nomes das atléticas
        atléticas_pontos_iguais = linhas_pontos_iguais['Atléticas'].tolist()
        if len(atléticas_pontos_iguais) == 2:
            team_ahead = df_confrontos_diretos.loc[atléticas_pontos_iguais[0], atléticas_pontos_iguais[1]]
            atléticas_pontos_iguais.remove(team_ahead)

            # Nome da atlética que você deseja trocar
            team_behind = atléticas_pontos_iguais[0]

            # Encontrar a posição da atlética no DataFrame
            position_ahead = df_group.index[df_group['Atléticas'] == team_ahead].tolist()[0]
            position_behind = df_group.index[df_group['Atléticas'] == team_behind].tolist()[0]

            # Trocar os valores entre as linhas diretamente
            df_group.loc[position_ahead], df_group.loc[position_behind] = df_group.loc[position_behind].copy(), df_group.loc[position_ahead].copy()

        return df_group.sort_values(by='Pontos', ascending=False)

    def update_df_games(new_game_data):
        global df_games
        df_games = pd.concat([df_games, pd.DataFrame([new_game_data])], ignore_index=True)

    def get_df_games_group(cls, group):
        df_games = cls.get_df_games()
        game_filter = df_games['GRUPO'] == group.upper()
        return df_games[game_filter]

    def get_df_ranking_group(group):
        try:
            df = pd.read_csv('files/group/ranking_' + group.upper() + '.csv')
            return df
        except FileNotFoundError:
            return jsonify({'error': str("O arquivo de dados não foi encontrado.")}), 404

    def update_confronto_direto(winner_team, loser_team, draw, confrontos_diretos):
        if draw:
            resultado = 'E'
        else:
            resultado = winner_team

        # Registrar o resultado no dicionário
        confrontos_diretos.setdefault(winner_team, {}).setdefault(loser_team, resultado)
        confrontos_diretos.setdefault(loser_team, {}).setdefault(winner_team, resultado)
        
        return confrontos_diretos

    def simulate_game(data_json, confrontos_diretos):
        
        home_team = data_json['home_team']
        away_team = data_json['away_team']

        if list_clashes(home_team, away_team).empty == False:
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
            df_group = get_df_ranking_group(group)

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
                update_confronto_direto(away_team, home_team, True, confrontos_diretos)
            elif home_goal > away_goal:
                df_group.loc[condition_home, 'Pontos'] += 3
                df_group.loc[condition_home, 'V'] += 1
                df_group.loc[condition_away, 'D'] += 1
                update_confronto_direto(home_team, away_team, False, confrontos_diretos)
            else:
                df_group.loc[condition_away, 'Pontos'] += 3
                df_group.loc[condition_away, 'V'] += 1
                df_group.loc[condition_home, 'D'] += 1
                update_confronto_direto(away_team, home_team, False, confrontos_diretos)

            update_df_games(game)
            update_ranking(group, confrontos_to_df(confrontos_diretos))
            return(game)
