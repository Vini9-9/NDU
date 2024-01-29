#!/usr/bin/env python
# coding: utf-8

# # Tabelas

import tabula
import pandas as pd
tables = tabula.read_pdf("files/Boletim.pdf", pages="70-71")
# print(tables)


# In[ ]:


tb_groupA = tables[3]
tb_groupB = tables[4]
tb_games = pd.concat([tables[1], tables[2]])
# print("Jogos:")
# print(tb_games)


# # Formatando as tabelas dos grupos

# In[ ]:


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


# print("Grupo A:")
# print(df_groupA)
# print("#########################################################################")
# print("Grupo B:")
# print(df_groupB)


# # Formatando tabela de jogos

# In[ ]:


df_games = pd.DataFrame(tb_games)

# Limpar os espaços extras e formatar a coluna 'DIA'
df_games['DIA'] = df_games['DIA'].str.replace(' ', '', regex=False)
df_games['DIA'] = pd.to_datetime(df_games['DIA'] + '/' + pd.to_datetime('now', utc=True).strftime('%Y'), format='%d/%m/%Y', errors='coerce')

# Limpar os espaços extras e corrigir a formatação dos placares
df_games['PLACAR'] = df_games['PLACAR'].str.replace(' ', '', regex=True)
df_games[['GOLS_MANDANTE', 'GOLS_VISITANTE']] = df_games['PLACAR'].str.split('X', expand=True)
df_games['SIMULADOR'] = False

# df_games


# ## Dicionário de correção

# ### Locais

# In[ ]:


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

# ### Atléticas participantes

teams_groupA = df_groupA['Atléticas'].tolist()
teams_groupB = df_groupB['Atléticas'].tolist()
teams = teams_groupA + teams_groupB
correction_teams = {
    'ESP M': 'ESPM',
    'MedicinaZ Taubaté': 'Medicina Taubaté',
    'Economia M ackenzie': 'Economia Mackenzie',
    'Economia M ackenzie': 'Economia Mackenzie',
    'FE I': 'FEI',
    'INSP ER': 'INSPER',
    'FEA U SP': 'FEA USP',
    'FEA P UC': 'FEA PUC',
    'Federaldo ABC': 'Federal do ABC',
    'FEC AP': 'FECAP',
    'Medicina Ta ubaté (DT)': 'Medicina Taubaté'
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
df_games['EQUIPE Mandante'] = df_games['EQUIPE Mandante'].apply(correct_team)
df_games['EQUIPE Visitante'] = df_games['EQUIPE Visitante'].apply(correct_team)


# # Jogos por grupo

# In[ ]:


filter_gamesA = df_games['GRUPO'] == 'A'
filter_gamesB = df_games['GRUPO'] == 'B'

gamesA = df_games[filter_gamesA]
gamesB = df_games[filter_gamesB]


def listar_jogos_por_time(team_surname):
  condition_home = df_games['EQUIPE Mandante'].str.contains(team_surname)
  condition_away = df_games['EQUIPE Visitante'].str.contains(team_surname)
  games_by_team = df_games[condition_home | condition_away]
  return games_by_team

def listar_confrontos(teamOne, teamTwo):
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

# # Jogos por data

def listar_jogos_por_data(game_date): #'2024-10-28'
  condition_date = df_games['DIA'] == game_date
  games_by_date = df_games[condition_date]
  games_by_date


# # Confronto direto


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

def gerar_confronto_direto(df_games):
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

def confrontos_to_df(confrontos_diretos):
  # Criar um DataFrame a partir dos resultados dos confrontos diretos
  df_confrontos_diretos = pd.DataFrame(confrontos_diretos).T.fillna('').sort_index()
  df_confrontos_diretos.index.name = 'Equipes'
  return df_confrontos_diretos


confrontos = gerar_confronto_direto(df_games)

# # Filtro com classificados

def atualizar_classificacao(group, df_confrontos_diretos):
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

  print(f"Classificação grupo {group} atualizada com confrontos diretos:")
  print(df_group.sort_values(by='Pontos', ascending=False))


# # Simulação

def atualizar_df_games(new_game_data):
    global df_games
    df_games = pd.concat([df_games, pd.DataFrame([new_game_data])], ignore_index=True)

def remover_df_games(matches_to_remove, simulador=True):
    # Obter os índices dos jogos a serem removidos
    indices_to_remove = matches_to_remove.index

    # Remover os jogos do DataFrame original
    df_games.drop(indices_to_remove, inplace=True)

# Simular o resultado do jogo (exemplo simples)
def simular_jogo(group, home_team, home_goal, away_team, away_goal, confrontos_diretos):
    
    if listar_confrontos(home_team, away_team).empty == False:
        print("Não posso substituir um jogo que já existe")
    else:
        game = {
            'GRUPO': group,
            'EQUIPE Mandante': home_team,
            'GOLS_MANDANTE': home_goal,
            'EQUIPE Visitante': away_team,
            'GOLS_VISITANTE': away_goal,
            'PLACAR': str(home_goal) + 'x' + str(away_goal),
            'SIMULADOR': 1
        }

        # Definir df por grupo
        if group == 'A':
          df_group = df_groupA
        elif group == 'B':
          df_group = df_groupB

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

        atualizar_df_games(game)
        atualizar_classificacao(group, confrontos_to_df(confrontos_diretos))

def remover_jogo(home_team, away_team, confrontos_diretos):

    df_confronto = listar_confrontos(home_team, away_team)
#   Se for jogo simulado  
    if df_confronto['SIMULADOR'].tolist()[0]:
        group = df_confronto['GRUPO'].values[0]

        # Definir df por grupo
        if group == 'A':
            df_group = df_groupA
        elif group == 'B':
            df_group = df_groupB

        home_team = df_confronto['EQUIPE Mandante'].tolist()[0]
        away_team = df_confronto['EQUIPE Visitante'].tolist()[0]
        home_goal = int(df_confronto['GOLS_MANDANTE'].tolist()[0])
        away_goal = int(df_confronto['GOLS_VISITANTE'].tolist()[0])

        condition_home = df_group['Atléticas'] == home_team
        condition_away = df_group['Atléticas'] == away_team

    # Atualizar o número de jogos
        df_group.loc[condition_home, 'Jogos'] -= 1
        df_group.loc[condition_away, 'Jogos'] -= 1

    # Atualizar os gols
        df_group.loc[condition_home, 'Gols Pró'] -= home_goal
        df_group.loc[condition_home, 'Gols Contra'] -= away_goal

        df_group.loc[condition_away, 'Gols Pró'] -= away_goal
        df_group.loc[condition_away, 'Gols Contra'] -= home_goal

        df_group.loc[condition_home, 'Saldo'] += home_goal - away_goal
        df_group.loc[condition_away, 'Saldo'] += away_goal - home_goal

    # Atualizar os pontos
        if home_goal == away_goal:
            df_group.loc[condition_home, 'Pontos'] -= 1
            df_group.loc[condition_away, 'Pontos'] -= 1
            df_group.loc[condition_home, 'E'] -= 1
            df_group.loc[condition_away, 'E'] -= 1
        elif home_goal > away_goal:
            df_group.loc[condition_home, 'Pontos'] -= 3
            df_group.loc[condition_home, 'V'] += 1
            df_group.loc[condition_away, 'D'] += 1
        else:
            df_group.loc[condition_away, 'Pontos'] -= 3
            df_group.loc[condition_away, 'V'] += 1
            df_group.loc[condition_home, 'D'] += 1

        remover_df_games(df_confronto)
        remover_confronto_direto(home_team, away_team, confrontos_diretos)
        atualizar_classificacao(group, confrontos_to_df(confrontos_diretos))
    else:
        print('Nenhum jogo simulado foi encontrado')

df_games.to_csv('files/games.csv', index=False)
print('df_games gerado')
df_groupA.to_csv('files/group/ranking_A.csv', index=False)
print('ranking_A gerado')
df_groupB.to_csv('files/group/ranking_B.csv', index=False)
print('ranking_B gerado')

# confrontos.to_csv('files/confrontos.csv', index=False)
confrontos_df = confrontos_to_df(confrontos).to_csv('files/confrontos_df.csv', index=False)