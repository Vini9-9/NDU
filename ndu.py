
import tabula
import pandas as pd
from flask import jsonify
import uuid
import csv
import json

import logging

# Configuração básica de logging
logging.basicConfig(filename='meu_arquivo_de_log.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Exemplo de uso do logging
# logging.info('Isso é uma mensagem de informação.')
# logging.warning('Isso é uma mensagem de aviso.')
# logging.error('Isso é uma mensagem de erro.')


def generate_game_id():
    return str(uuid.uuid4())

def load_json_data(filepath):
    """
    Carrega os dados de um arquivo JSON.

    :param filepath: O caminho para o arquivo JSON.
    :return: Os dados carregados do arquivo JSON.
    """
    with open(filepath, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def create_json(data, json_file):
    with open(json_file, 'w', encoding='utf-8') as file:  # Certifique-se de especificar a codificação correta
        json.dump(data, file, indent=4, ensure_ascii=False)  # Especifica ensure_ascii=False para lidar com acentos
    
    logging.info('criado JSON em ' + json_file)

def csv_to_json(csv_file, json_file):
    """
    Converte um arquivo CSV em um arquivo JSON.

    :param csv_file: Caminho para o arquivo CSV.
    :param json_file: Caminho para o arquivo JSON de saída.
    """
    # Lista para armazenar os dados do CSV
    data = []

    # Lendo o arquivo CSV e populando a lista de dados
    with open(csv_file, 'r', encoding='utf-8') as file:  # Certifique-se de especificar a codificação correta
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            data.append(row)

    # Escrevendo os dados em um arquivo JSON
    create_json(data, json_file)

# %%
def create_games_files(df_games, filepath):
    csv_file = filepath +'/games.csv'
    json_file = filepath +'/games.json'
    df_games.to_csv(csv_file, index=False)
    csv_to_json(csv_file, json_file)

# %% [markdown]
# # Criando tabela dos grupos

# %%
def create_zero_ranking_group(table_groups, filepath):
    teams_groupA = table_groups['Grupo A'].tolist()
    teams_groupB = table_groups['Grupo B'].tolist()
    # Criar DataFrames vazios com as colunas necessárias
    columns = ['Time', 'Pontos', 'Jogos', 'V', 'E', 'D', 'Gols_Pro', 'Gols_Contra', 'Saldo']
    df_groupA = pd.DataFrame(columns=columns)
    df_groupB = pd.DataFrame(columns=columns)

    # Adicionar nomes dos grupos
    df_groupA['Time'] = teams_groupA
    df_groupB['Time'] = teams_groupB

    # Inicializar outras colunas com zeros
    for col in columns[1:]:
        df_groupA[col] = 0
        df_groupB[col] = 0

    # Define o tipo de dados para as colunas
    dtypes = {'Pontos': int, 'Jogos': int, 'V': int, 'E': int, 'D': int, 'Gols_Pro': int, 'Gols_Contra': int, 'Saldo': int}
    df_groupA = df_groupA.astype(dtypes)
    df_groupB = df_groupB.astype(dtypes)
    df_groupA['ID'] = [generate_game_id() for _ in range(len(df_groupA))]
    df_groupB['ID'] = [generate_game_id() for _ in range(len(df_groupB))]
    
    df_groupA.to_csv(filepath + '/ranking_A.csv', index=False)
    df_groupB.to_csv(filepath  + '/ranking_B.csv', index=False)
    
    csv_to_json(filepath  + '/ranking_A.csv', filepath + '/ranking_A.json')
    csv_to_json(filepath + '/ranking_B.csv', filepath + '/ranking_B.json')

    return df_groupA, df_groupB

# %% [markdown]
# # Formatando as tabelas dos grupos

# %%
def format_table_group(tb_groupA, tb_groupB):
    df_groupA_base = pd.DataFrame(tb_groupA)
    df_groupB_base = pd.DataFrame(tb_groupB)

    # Atualizando nome das colunas:
    novos_nomes_colunas = ['Col.', 'Atléticas', 'Pontos', 'Jogos', 'V', 'E', 'D', 'Gols Pró', 'Gols Contra', 'Saldo']
    df_groupA_base.columns = novos_nomes_colunas
    df_groupB_base.columns = novos_nomes_colunas


    # Removendo a primeira coluna
    df_groupA = df_groupA_base.drop(columns=['Col.'])
    df_groupB = df_groupB_base.drop(columns=['Col.'])

    # Removendo as duas primeiras linhas (antiga coluna)
    df_groupA.drop([0, 1], inplace=True)
    df_groupB.drop([0, 1], inplace=True)


    # Converter os dados das colunas para o tipo int
    colunas_para_converter = ['Pontos', 'Jogos', 'V', 'E', 'D', 'Gols Pró', 'Gols Contra', 'Saldo']
    df_groupA[colunas_para_converter] = df_groupA[colunas_para_converter].astype(int)
    df_groupB[colunas_para_converter] = df_groupB[colunas_para_converter].astype(int)

# %% [markdown]
# # Formatando tabela de jogos

# %%
def generate_table_games(tb_games):
    df_games = pd.DataFrame(tb_games)
    if df_games['DIA'].isna().all():
        df_games['DIA'] = ''
    else:
        # Limpar os espaços extras e formatar a coluna 'DIA'
        df_games['DIA'] = df_games['DIA'].str.replace(' ', '', regex=False)
        df_games['DIA'] = pd.to_datetime(df_games['DIA'] + '/' + pd.to_datetime('now', utc=True).strftime('%Y'), format='%d/%m/%Y', errors='coerce')

    # Limpar os espaços extras e corrigir a formatação dos placares
    df_games['PLACAR'] = df_games['PLACAR'].str.replace(' ', '', regex=True)
    df_games[['GOLS_MANDANTE', 'GOLS_VISITANTE']] = df_games['PLACAR'].str.split('X', expand=True)
    df_games['SIMULADOR'] = False
    df_games.rename(columns={'HORÁRIO': 'HORARIO'}, inplace=True)
    df_games.rename(columns={'EQUIPE Mandante': 'Mandante'}, inplace=True)
    df_games.rename(columns={'EQUIPE Visitante': 'Visitante'}, inplace=True)
    
    return df_games

# %% [markdown]
# # Jogos por time

# %%
def listar_jogos_por_time(df_games, team_surname):
  condition_home = df_games['EQUIPE Mandante'].str.contains(team_surname)
  condition_away = df_games['EQUIPE Visitante'].str.contains(team_surname)
  games_by_team = df_games[condition_home | condition_away]
  return games_by_team

def listar_confrontos(df_games, teamOne, teamTwo):
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

# %% [markdown]
# # Confronto direto

# %%
def update_confronto_direto(winner_team, loser_team, draw, confrontos_diretos):
   if draw:
      resultado = 'E'
   else:
      resultado = winner_team

  # Registrar o resultado no dicionário
   confrontos_diretos.setdefault(winner_team, {}).setdefault(loser_team, resultado)
   confrontos_diretos.setdefault(loser_team, {}).setdefault(winner_team, resultado)
   return confrontos_diretos

def remover_confronto_direto(winner_team, loser_team, confrontos_diretos):
  # Registrar o resultado no dicionário
   confrontos_diretos.setdefault(winner_team, {}).setdefault(loser_team, '')
   confrontos_diretos.setdefault(loser_team, {}).setdefault(winner_team, '')
   return confrontos_diretos

def gerar_confronto_direto(df_games, filepath):
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

  create_json(confrontos_diretos, filepath + '/confrontation.json')

  return confrontos_diretos

def confrontos_to_df(confrontos_diretos):
  # Criar um DataFrame a partir dos resultados dos confrontos diretos
  df_confrontos_diretos = pd.DataFrame(confrontos_diretos).T.fillna('').sort_index()
  df_confrontos_diretos.index.name = 'Equipes'
  return df_confrontos_diretos

def tem_ranking(df_group):
    elemento = df_group.iloc[2, 1] # Time na Posição 1o Colocado
    return pd.isna(elemento) == False

# %%
def atualizar_classificacao(df_group, df_confrontos_diretos, group):

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

  logging.info(f"Classificação grupo {group} atualizada com confrontos diretos:")
#   print(df_group.sort_values(by='Pontos', ascending=False))

# %% [markdown]
# # Simulação

# %%
def atualizar_df_games(new_game_data):
    global df_games
    df_games = pd.concat([df_games, pd.DataFrame([new_game_data])], ignore_index=True)

def remover_df_games(matches_to_remove, simulador=True):
    # Obter os índices dos jogos a serem removidos
    indices_to_remove = matches_to_remove.index

    # Remover os jogos do DataFrame original
    df_games.drop(indices_to_remove, inplace=True)

# Simular o resultado do jogo (exemplo simples)
# def simular_jogo(group, home_team, home_goal, away_team, away_goal, confrontos_diretos):
    
#     if listar_confrontos(home_team, away_team).empty == False:
#         print("Não posso substituir um jogo que já existe")
#     else:
#         game = {
#             'GRUPO': group,
#             'EQUIPE Mandante': home_team,
#             'GOLS_MANDANTE': home_goal,
#             'EQUIPE Visitante': away_team,
#             'GOLS_VISITANTE': away_goal,
#             'PLACAR': str(home_goal) + 'x' + str(away_goal),
#             'SIMULADOR': 1
#         }

#         # Definir df por grupo
#         if group == 'A':
#           df_group = df_groupA
#         elif group == 'B':
#           df_group = df_groupB

#         condition_home = df_group['Atléticas'] == home_team
#         condition_away = df_group['Atléticas'] == away_team

#     # Atualizar o número de jogos
#         df_group.loc[condition_home, 'Jogos'] += 1
#         df_group.loc[condition_away, 'Jogos'] += 1

#     # Atualizar os gols
#         df_group.loc[condition_home, 'Gols Pró'] += home_goal
#         df_group.loc[condition_home, 'Gols Contra'] += away_goal

#         df_group.loc[condition_away, 'Gols Pró'] += away_goal
#         df_group.loc[condition_away, 'Gols Contra'] += home_goal

#         df_group.loc[condition_home, 'Saldo'] += home_goal - away_goal
#         df_group.loc[condition_away, 'Saldo'] += away_goal - home_goal

#     # Atualizar os pontos
#         if home_goal == away_goal:
#             df_group.loc[condition_home, 'Pontos'] += 1
#             df_group.loc[condition_away, 'Pontos'] += 1
#             df_group.loc[condition_home, 'E'] += 1
#             df_group.loc[condition_away, 'E'] += 1
#             update_confronto_direto(away_team, home_team, True, confrontos_diretos)
#         elif home_goal > away_goal:
#             df_group.loc[condition_home, 'Pontos'] += 3
#             df_group.loc[condition_home, 'V'] += 1
#             df_group.loc[condition_away, 'D'] += 1
#             update_confronto_direto(home_team, away_team, False, confrontos_diretos)
#         else:
#             df_group.loc[condition_away, 'Pontos'] += 3
#             df_group.loc[condition_away, 'V'] += 1
#             df_group.loc[condition_home, 'D'] += 1
#             update_confronto_direto(away_team, home_team, False, confrontos_diretos)

#         atualizar_df_games(game)
#         atualizar_classificacao(group, confrontos_to_df(confrontos_diretos))

# %%
# def remover_jogo(home_team, away_team, confrontos_diretos):

#     df_confronto = listar_confrontos(home_team, away_team)
# #   Se for jogo simulado  
#     if df_confronto['SIMULADOR'].tolist()[0]:
#         group = df_confronto['GRUPO'].values[0]

#         # Definir df por grupo
#         if group == 'A':
#             df_group = df_groupA
#         elif group == 'B':
#             df_group = df_groupB

#         home_team = df_confronto['EQUIPE Mandante'].tolist()[0]
#         away_team = df_confronto['EQUIPE Visitante'].tolist()[0]
#         home_goal = int(df_confronto['GOLS_MANDANTE'].tolist()[0])
#         away_goal = int(df_confronto['GOLS_VISITANTE'].tolist()[0])

#         condition_home = df_group['Atléticas'] == home_team
#         condition_away = df_group['Atléticas'] == away_team

#     # Atualizar o número de jogos
#         df_group.loc[condition_home, 'Jogos'] -= 1
#         df_group.loc[condition_away, 'Jogos'] -= 1

#     # Atualizar os gols
#         df_group.loc[condition_home, 'Gols Pró'] -= home_goal
#         df_group.loc[condition_home, 'Gols Contra'] -= away_goal

#         df_group.loc[condition_away, 'Gols Pró'] -= away_goal
#         df_group.loc[condition_away, 'Gols Contra'] -= home_goal

#         df_group.loc[condition_home, 'Saldo'] += home_goal - away_goal
#         df_group.loc[condition_away, 'Saldo'] += away_goal - home_goal

#     # Atualizar os pontos
#         if home_goal == away_goal:
#             df_group.loc[condition_home, 'Pontos'] -= 1
#             df_group.loc[condition_away, 'Pontos'] -= 1
#             df_group.loc[condition_home, 'E'] -= 1
#             df_group.loc[condition_away, 'E'] -= 1
#         elif home_goal > away_goal:
#             df_group.loc[condition_home, 'Pontos'] -= 3
#             df_group.loc[condition_home, 'V'] += 1
#             df_group.loc[condition_away, 'D'] += 1
#         else:
#             df_group.loc[condition_away, 'Pontos'] -= 3
#             df_group.loc[condition_away, 'V'] += 1
#             df_group.loc[condition_home, 'D'] += 1

#         remover_df_games(df_confronto)
#         remover_confronto_direto(home_team, away_team, confrontos_diretos)
#         atualizar_classificacao(group, confrontos_to_df(confrontos_diretos))
#     else:
#         print('Nenhum jogo simulado foi encontrado')
# %% [markdown]
# ### Dicionário de correção
def verificar_listagem(set_output, set_default):
    elementos_ausentes = set(set_output) - set(set_default)
    if len(elementos_ausentes) > 0:
        logging.warning("Os seguintes elementos não estão listados:")
        logging.warning(elementos_ausentes)

def corrigir_local(df_games):
    locations = ['Palestra', 'Idalina', 'Pinheiros', 'SEMEF', 'GETA', 'EDA', 'CESPRO']
    correction_local = {
        'Pale stra': 'Palestra',
        'Idal ina': 'Idalina',
        'SEM EF': 'SEMEF',
    }
    # Função de validação e correção
    def correct_local(local):
        if local in locations:
            return local
        elif local in correction_local:
            return correction_local[local]
        else:
            return local

    # Aplicar a função de validação e correção nas colunas 'EQUIPE Mandante' e 'EQUIPE Visitante'
    df_games['LOCAL'] = df_games['LOCAL'].apply(correct_local)
    verificar_listagem(df_games['LOCAL'].unique(), locations)
    return df_games

def corrigir_times(tb_group, df_games): 
    teams_groupA = tb_group['Grupo A'].tolist()
    teams_groupB = tb_group['Grupo B'].tolist()
    teams = teams_groupA + teams_groupB
    correction_teams = {
        'ArquiteturaMackenzie': 'Arquitetura Mackenzie',
        'Belas A rtes': 'Belas Artes',
        'CAAP U FABC': 'CAAP UFABC',
        'Comunica ção PUC': 'Comunicação PUC',
        'Comunicaçã o Anhembi': 'Comunicação Anhembi',
        'Comunicaçã o Mackenzie': 'Comunicação Mackenzie',
        'Comunicaçã o Metodista': 'Comunicação Metodista',
        'Direit o PUC': 'Direito PUC',
        'Direit o USP': 'Direito USP',
        'Direito M ackenzie': 'Direito Mackenzie',
        'Direito S ã o Judas': 'Direito São Judas',
        'Direito S ão Judas': 'Direito São Judas',
        'Direito SãoBernardo': 'Direito São Bernardo',
        'EACHUSP': 'EACH USP',
        'EEFEUSP': 'EEFE USP',
        'Economia M ackenzie': 'Economia Mackenzie',
        'Economia M ackenzie': 'Economia Mackenzie',
        'Educação Fís i ca Anhembi': 'Educação Física Anhembi',
        'Educação Fís i ca UNINOVE': 'Educação Física UNINOVE',
        'Educação Fís ica Anhembi': 'Educação Física Anhembi',
        'EngenhariaAnhembi': 'Engenharia Anhembi',
        'EngenhariaMackenzie': 'Engenharia Mackenzie',
        'EngenhariaSão Judas': 'Engenharia São Judas',
        'EngenhariaUNICAMP': 'Engenharia UNICAMP',
        'ESP M': 'ESPM',
        'Farmác ia USP': 'Farmácia USP',
        'Fatec Sã o Paulo': 'Fatec São Paulo',
        'FAUUSP': 'FAU USP',
        'FAA P': 'FAAP',
        'FE I': 'FEI',
        'FEA P UC': 'FEA PUC',
        'FEA U SP': 'FEA USP',
        'FEC AP': 'FECAP',
        'Federaldo ABC': 'Federal do ABC',
        'FM U': 'FMU',
        'GetúlioVargas': 'Getúlio Vargas',
        'IBME C SP': 'IBMEC SP',
        'INS P ER': 'INSPER',
        'INSP ER': 'INSPER',
        'IT A': 'ITA',
        'IME U SP': 'IME USP',
        'DireitoFMU': 'Direito FMU',
        'LEP Mac kenzie': 'LEP Mackenzie',
        'LEP MAC KENZIE': 'LEP MACKENZIE',
        'Ma uá': 'Mauá',
        'MedicinaPaulista': 'Medicina Paulista',
        'Medici n a USP': 'Medicina USP',
        'Medicin a ABC': 'Medicina ABC',
        'Medici n a ABC': 'Medicina ABC',
        'Medicin a ABC': 'Medicina ABC',
        'Medicin a Santos': 'Medicina Santos',
        'Medicina PU C Campinas': 'Medicina PUC Campinas',
        'Medicina S ã o Caetano': 'Medicina São Caetano',
        'Medicina S anta Casa': 'Medicina Santa Casa',
        'Medicina Sa nto Amaro': 'Medicina Santo Amaro',
        'Medicina Sã o Bernardo': 'Medicina São Bernardo',
        'Medicina Sã o Caetano': 'Medicina São Caetano',
        'Medicina San  ta Marcelina': 'Medicina Santa Marcelina',
        'Medicina San ta Marcelina': 'Medicina Santa Marcelina',
        'Medicina Ta ubaté (DT)': 'Medicina Taubaté',
        'Medicina U NICAMP': 'Medicina UNICAMP',
        'Medicina U NINOVE': 'Medicina UNINOVE',
        'MedicinaAnhembi': 'Medicina Anhembi',
        'MedicinaBragança': 'Medicina Bragança',
        'MedicinaEinstein': 'Medicina Einstein',
        'MedicinaJundiaí': 'Medicina Jundiaí',
        'MedicinaTaubaté': 'Medicina Taubaté',
        'MedicinaUNICID': 'Medicina UNICID',
        'MedicinaUNIMES': 'Medicina UNIMES',
        'MedicinaZ Taubaté': 'Medicina Taubaté',
        'Politécn ica USP': 'Politécnica USP',
        'Psicologia  d a PUC SP': 'Psicologia da PUC SP',
        'Psicologia d a PUC SP': 'Psicologia da PUC SP',
        'SEN  AC': 'SENAC',
        'SEN AC': 'SENAC',
        'Sistema de Inf ormação USP': 'Sistema de Informação USP',
        'UN IP': 'UNIP',
        'UNIFESP D iadema': 'UNIFESP Diadema',
        'Unifesp S ão Paulo': 'Unifesp São Paulo',
        'UNIFESPOsasco': 'UNIFESP Osasco',
        'US C S': 'USCS',
        'US CS': 'USCS',
        'Veteriná ria USP': 'Veterinária USP',
    }
    # Função de validação e correção
    def correct_team(equipe):
        equipe_strip = equipe.strip().replace('  ', ' ')
        if equipe_strip in teams:
            return equipe_strip
        elif equipe_strip in correction_teams:
            return correction_teams[equipe_strip]
        else:
            return equipe_strip

    # Aplicar a função de validação e correção nas colunas 'EQUIPE Mandante' e 'EQUIPE Visitante'
    df_games['Mandante'] = df_games['Mandante'].apply(correct_team)
    df_games['Visitante'] = df_games['Visitante'].apply(correct_team)
    times_output = set(df_games['Mandante'].unique()) | set(df_games['Visitante'].unique())
    verificar_listagem(times_output, teams)
    return df_games

def atualizar_dados_times(df_nova, df_original):
    # Salvar a coluna 'ID' em uma variável temporária
    id_column = df_original.pop('ID')

    # Redefinir o índice do DataFrame df_original
    df_original.reset_index(inplace=True)

    # Atualizar os dados em df_original com base em df_nova
    for index, row in df_nova.iterrows():
        time = row['Time']
        idx = df_original[df_original['Time'] == time].index
        if not idx.empty:
            df_original.loc[idx[0]] = row

    # Reatribuir a coluna 'ID' ao DataFrame df_original
    df_original['ID'] = id_column

    # Agora, df_original contém os dados atualizados
    return df_original

def get_rankings_zero_group(modality):
    ranking_A = load_json_data(f'files/{modality}/group/ranking_zero_A.json')
    ranking_B = load_json_data(f'files/{modality}/group/ranking_zero_B.json')
    return {
        'A': ranking_A,
        'B': ranking_B
    }

def get_index_teams(rankings):
    ranking_dict_A = {time_dict['Time']: index for index, time_dict in enumerate(rankings['A'])}
    ranking_dict_B = {time_dict['Time']: index for index, time_dict in enumerate(rankings['B'])}
    return {
        'A': ranking_dict_A,
        'B': ranking_dict_B
    }

def generate_ranking_by_games(modality):
    
    json_games = load_json_data(f'files/{modality}/games.json')
    rankings = get_rankings_zero_group(modality)
    index_teams = get_index_teams(rankings)

    # Percorra cada jogo no DataFrame df_games
    for jogo in json_games:
        if jogo["PLACAR"] == "X":
            continue
        grupo = jogo["GRUPO"]
        mandante = jogo["Mandante"]
        visitante = jogo["Visitante"]
        dados_ranking_mandante = rankings[grupo][index_teams[grupo][mandante]]
        dados_ranking_visitante = rankings[grupo][index_teams[grupo][visitante]]
        placar_mandante = int(jogo["GOLS_MANDANTE"]) 
        placar_visitante = int(jogo["GOLS_VISITANTE"])
        
        # Atualize os pontos das equipes com base no resultado do jogo
        if placar_mandante > placar_visitante:
            dados_ranking_mandante['Pontos'] = int(dados_ranking_mandante['Pontos']) + 3
            dados_ranking_mandante['V'] = int(dados_ranking_mandante['V']) + 1
            dados_ranking_visitante['D'] = int(dados_ranking_visitante['D']) + 1
            
        
        elif placar_mandante == placar_visitante:
            dados_ranking_mandante['Pontos'] = int(dados_ranking_mandante['Pontos']) + 1
            dados_ranking_visitante['Pontos'] = int(dados_ranking_visitante['Pontos']) + 1
            dados_ranking_mandante['E'] = int(dados_ranking_mandante['E']) + 1
            dados_ranking_visitante['E'] = int(dados_ranking_visitante['E']) + 1
            
        else:
            dados_ranking_visitante['Pontos'] = int(dados_ranking_visitante['Pontos']) + 3
            dados_ranking_visitante['V'] = int(dados_ranking_visitante['V']) + 1
            dados_ranking_mandante['D'] = int(dados_ranking_mandante['D']) + 1

        dados_ranking_mandante['Jogos'] = int(dados_ranking_mandante['Jogos']) + 1
        dados_ranking_visitante['Jogos'] = int(dados_ranking_visitante['Jogos']) + 1
        
        
        dados_ranking_mandante['Gols_Pro'] = int(dados_ranking_mandante['Gols_Pro']) + placar_mandante
        dados_ranking_visitante['Gols_Pro'] = int(dados_ranking_visitante['Gols_Pro']) + placar_visitante
        
        dados_ranking_mandante['Gols_Contra'] = int(dados_ranking_mandante['Gols_Contra']) + placar_visitante
        dados_ranking_visitante['Gols_Contra'] = int(dados_ranking_visitante['Gols_Contra']) + placar_mandante

        dados_ranking_mandante['Saldo'] = int(dados_ranking_mandante['Gols_Pro']) - int(dados_ranking_mandante['Gols_Contra'])
        dados_ranking_visitante['Saldo'] = int(dados_ranking_visitante['Gols_Pro']) - int(dados_ranking_visitante['Gols_Contra'])
        
    return rankings

def update_ranking(tb_groups, df_confrontos_diretos):
  df_groups = []
  idx = 1
  columns_to_convert = ['Pontos', 'Jogos', 'V', 'E', 'D', 'Gols_Pro', 'Gols_Contra', 'Saldo']
  
  for tb_group in tb_groups: 
    df_group = pd.DataFrame(tb_group)
    df_group[columns_to_convert] = df_group[columns_to_convert].astype(int)
    df_group.sort_values(by=['Pontos', 'Saldo', 'Gols_Pro'], ascending=[False, False, False], inplace=True)
    df_group.reset_index(drop=True, inplace=True)
    pontos_iguais = df_group['Pontos'].unique().tolist()

    for ponto in pontos_iguais:
      times_pontos_iguais = df_group[df_group['Pontos'] == ponto]['Time'].tolist()
      if len(times_pontos_iguais) == 2:
        logging.info('times_pontos_iguais:', times_pontos_iguais)
        team_ahead = df_confrontos_diretos.loc[times_pontos_iguais[0], times_pontos_iguais[1]]
        if team_ahead != 'E' and team_ahead != '':
          times_pontos_iguais.remove(team_ahead)

          # Nome da atlética que você deseja trocar
          team_behind = times_pontos_iguais[0]

          # Encontrar a posição da atlética no DataFrame
          position_ahead = df_group.index[df_group['Time'] == team_ahead].tolist()[0]
          position_behind = df_group.index[df_group['Time'] == team_behind].tolist()[0]
          if position_ahead > position_behind:
              # Trocar os valores entre as linhas diretamente
              df_group.loc[position_ahead], df_group.loc[position_behind] = df_group.loc[position_behind].copy(), df_group.loc[position_ahead].copy()
              
    df_groups.append(df_group)
    idx = idx + 1
  return df_groups


def format_tb_group(tb_group):
    if list(tb_group.columns) != ['Grupo A', 'Grupo B']:
        # Definir a primeira linha como cabeçalho da tabela
        tb_group.columns = tb_group.iloc[0]
        # Remover a primeira linha, que agora é o cabeçalho
        return tb_group[1:]
# %% [markdown]
# # Execução

def execute_zero_ranking(dic_modalities_page):

    for key, value in dic_modalities_page.items():
        logging.info(f"modalidade: {key}")
        modality = key
        # tables = tabula.read_pdf("files/Boletim.pdf", pages=dic_modalities_page[modality])
        tables = tabula.read_pdf("files/Boletim.pdf", pages=value)
        print(tables)
        tb_group = format_tb_group(tables[0])
        tb_games = tables[1]

        filepath = 'files/' + modality
        filepath_group = filepath + '/group'
        rankings = create_zero_ranking_group(tb_group, filepath_group)
        df_games = generate_table_games(tb_games)
        df_games = corrigir_local(df_games)
        df_games = corrigir_times(tb_group, df_games)
        create_games_files(df_games, filepath)
        gerar_confronto_direto(df_games, filepath)

def execute_update_data_by_modality(modality, pages):
    logging.info(f"modalidade: {modality}")
    tables = tabula.read_pdf("files/Boletim.pdf", pages=pages)
    tb_group = format_tb_group(tables[0])
    tb_games = tables[1]

    filepath = 'files/' + modality
    # filepath_group = filepath + '/group'
    df_games = generate_table_games(tb_games)
    df_games = corrigir_local(df_games)
    df_games = corrigir_times(tb_group, df_games)
    create_games_files(df_games, filepath)
    confrontos = gerar_confronto_direto(df_games, filepath)
    df_confrontos_diretos = confrontos_to_df(confrontos)
    rankings = generate_ranking_by_games(modality)
    df_groups = update_ranking([rankings['A'], rankings['B']], df_confrontos_diretos)
    df_groupA = df_groups[0]
    df_groupB = df_groups[1]

    df_groupA.to_csv(f'files/{modality}/group/ranking_A.csv', index=False)
    df_groupB.to_csv(f'files/{modality}/group/ranking_B.csv', index=False)

    csv_to_json(f'files/{modality}/group/ranking_A.csv', f'files/{modality}/group/ranking_A.json')
    csv_to_json(f'files/{modality}/group//ranking_B.csv', f'files/{modality}/group/ranking_B.json')

def execute_update_data(dic_modalities_page):

    for key, value in dic_modalities_page.items():
        execute_update_data_by_modality(key, value)
        logging.info("----------------------------------------")

dic_modalities_page = {
        "FF/A" : "42-43",
        "FF/B" : "46-47",
        "FF/C" : "50-51",
        "FF/D" : "54-55",
        "FF/E" : "58-59",
        "FM/A" : "62-63",
        "FM/B" : "66-67",
        "FM/C" : "70-71",
        "FM/D" : "74-75",
        "FM/E" : "78-79",
        "FM/F" : "82-83",
    }

execute_update_data(dic_modalities_page)