
import tabula
import pandas as pd
import uuid
import csv
import json

import datetime
import logging
import inspect

data_hora_atual = datetime.datetime.now()

dia_atual = data_hora_atual.date()

# Configuração básica de logging
logging.basicConfig(filename='logs/log_ndu_' + data_hora_atual.strftime("%Y-%m-%d_%H-%M-%S") + '.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logging.basicConfig(filename='logs/debug_ndu_' + data_hora_atual.strftime("%Y-%m-%d_%H-%M-%S") + '.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def log_function_entry():
    function_name = inspect.currentframe().f_back.f_code.co_name
    logging.debug(f"Function: {function_name}")

def generate_game_id():
    return str(uuid.uuid4())

def load_json_data(filepath):
    log_function_entry()
    """
    Carrega os dados de um arquivo JSON.

    :param filepath: O caminho para o arquivo JSON.
    :return: Os dados carregados do arquivo JSON.
    """
    with open(filepath, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def create_json(data, json_file):
    log_function_entry()
    with open(json_file, 'w', encoding='utf-8') as file:  # Certifique-se de especificar a codificação correta
        json.dump(data, file, indent=4, ensure_ascii=False)  # Especifica ensure_ascii=False para lidar com acentos
    
    logging.info('criado JSON em ' + json_file)

def csv_to_json(csv_file, json_file):
    log_function_entry()
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

def convert_to_json_serializable(value):
    """
    Converte um valor para um tipo que pode ser serializado em JSON.
    
    :param value: Valor a ser convertido.
    :return: Valor convertido para um tipo serializável em JSON.
    """
    if isinstance(value, pd.Timestamp):
        return value.strftime('%Y-%m-%d')  # Formato YYYY-MM-DD
    elif pd.isna(value):  # Lida com NaN, NaT e None
        return None
    elif isinstance(value, (list, dict, str, int, float, bool)):
        return value
    else:
        # Converte outros tipos para string, se necessário
        return str(value)

def create_json_from_df(df, json_file):
    """
    Converte um DataFrame em um arquivo JSON.

    :param df: DataFrame a ser convertido.
    :param json_file: Caminho para o arquivo JSON de saída.
    """
    log_function_entry()

    # Aplicar a conversão para cada valor do DataFrame
    df = df.map(convert_to_json_serializable)

    # Converter DataFrame para lista de dicionários
    data = df.to_dict(orient='records')
    create_json(data, json_file)

def save_json_data(data, file_path):
    log_function_entry()
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def create_files(df_games, filepath, filename='games'):
    log_function_entry()
    full_filepath=f'{filepath}/{filename}'
    # csv_file = f"{full_filepath}.csv"
    json_file = f"{full_filepath}.json"
    # df_games.to_csv(csv_file, index=False)
    # csv_to_json(csv_file, json_file)
    # json_data = df_games.to_dict(orient='records')
    # create_json(json_data, json_file)
    create_json_from_df(df_games, json_file)

# Criando tabela dos grupos
def create_zero_ranking_group(table_groups, filepath):
    log_function_entry()
    dataframes = []
    
    header_zero = table_groups.columns[0]
    if 'grupo' not in header_zero.lower():
        logging.warning(f"header_zero inválido: {header_zero}")
        logging.info(f"Colocando o header atual na última linha")
        # Adicionar os cabeçalhos atuais à última linha de valores de cada coluna
        table_groups.loc[len(table_groups)+1] = table_groups.columns

        num_cols = table_groups.shape[1]
        new_headers = [f'Grupo {chr(65 + i)}' for i in range(num_cols)]

        logging.info(f"Atualizando headers")
        # Atualizar os cabeçalhos do DataFrame
        table_groups.columns = new_headers

    for group in ['Grupo A', 'Grupo B', 'Grupo C']:
        if group in table_groups:
            teams = table_groups[group].tolist()

            # Criar DataFrame vazio com as colunas necessárias
            columns = ['Time', 'Pontos', 'Jogos', 'V', 'E', 'D', 'Gols_Pro', 'Gols_Contra', 'Saldo']
            df_group = pd.DataFrame(columns=columns)
            
            # Adicionar nomes dos grupos
            df_group['Time'] = teams

            # Inicializar outras colunas com zeros
            for col in columns[1:]:
                df_group[col] = 0

            # Define o tipo de dados para as colunas
            dtypes = {'Pontos': int, 'Jogos': int, 'V': int, 'E': int, 'D': int, 'Gols_Pro': int, 'Gols_Contra': int, 'Saldo': int}
            df_group = df_group.astype(dtypes)
            df_group['ID'] = [generate_game_id() for _ in range(len(df_group))]

            # Adicionar DataFrame à lista
            dataframes.append((group, df_group))

            # Salvar em JSON
            group_letter = group.split()[-1]
            json_data = df_group.to_dict(orient='records')
            create_json(json_data, f"{filepath}/ranking_zero_{group_letter}.json")
        
    return dataframes

# Formatando as tabelas dos grupos
def format_table_group(tb_groupA, tb_groupB):
    log_function_entry()
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

# Formatando tabela de jogos
def check_simulador(row):
    log_function_entry()
    
    dia_jogo = pd.to_datetime(row['DIA'], format='%Y-%m-%d', errors='coerce').date()

    if pd.isna(dia_jogo) or dia_jogo > dia_atual or row['PLACAR'] == 'X':
        row['PLACAR'] = 'X'
        row['GOLS_MANDANTE'] = ''
        row['GOLS_VISITANTE'] = ''
        return True
    else:
        return False   
    
def verify_empty_games(tables):
    log_function_entry()
    for df in tables:
        # Verificar se 'EQUIPE Mandante' é NaN
        empty_rows = df[df['EQUIPE Mandante'].isna()]

        # Remover as linhas onde 'EQUIPE Mandante' ou 'EQUIPE Visitante' é NaN
        if not empty_rows.empty:
            df.dropna(subset=['EQUIPE Mandante'], inplace=True)
    
    concatenated_df = pd.concat(tables, ignore_index=True)
    return concatenated_df

def generate_table_games(tables):
    log_function_entry()
    tb_games = verify_empty_games(tables)
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
    df_games['ID'] = [generate_game_id() for _ in range(len(df_games))]
    df_games.rename(columns={'HORÁRIO': 'HORARIO'}, inplace=True)
    df_games.rename(columns={'EQUIPE Mandante': 'Mandante'}, inplace=True)
    df_games.rename(columns={'EQUIPE Visitante': 'Visitante'}, inplace=True)
    df_games['SIMULADOR'] = False
    return df_games

# Jogos por time
def listar_jogos_por_time(df_games, team_surname):
    log_function_entry()
    condition_home = df_games['EQUIPE Mandante'].str.contains(team_surname)
    condition_away = df_games['EQUIPE Visitante'].str.contains(team_surname)
    games_by_team = df_games[condition_home | condition_away]
    return games_by_team

def listar_confrontos(df_games, teamOne, teamTwo):
    log_function_entry()
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

# Confronto direto
def update_confronto_direto(winner_team, loser_team, draw, confrontos_diretos):
    log_function_entry()
    if draw:
        resultado = 'E'
    else:
        resultado = winner_team

    # Registrar o resultado no dicionário
    confrontos_diretos.setdefault(winner_team, {}).setdefault(loser_team, resultado)
    confrontos_diretos.setdefault(loser_team, {}).setdefault(winner_team, resultado)
    return confrontos_diretos

def remover_confronto_direto(winner_team, loser_team, confrontos_diretos):
    log_function_entry()
    # Registrar o resultado no dicionário
    confrontos_diretos.setdefault(winner_team, {}).setdefault(loser_team, '')
    confrontos_diretos.setdefault(loser_team, {}).setdefault(winner_team, '')
    return confrontos_diretos

def gerar_confronto_direto(df_games, filepath):
    log_function_entry()
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
    log_function_entry()
    # Criar um DataFrame a partir dos resultados dos confrontos diretos
    df_confrontos_diretos = pd.DataFrame(confrontos_diretos).T.fillna('').sort_index()
    df_confrontos_diretos.index.name = 'Equipes'
    return df_confrontos_diretos

def tem_ranking(df_group):
    log_function_entry()
    elemento = df_group.iloc[2, 1] # Time na Posição 1o Colocado
    return pd.isna(elemento) == False

def atualizar_classificacao(df_group, df_confrontos_diretos, group):
    log_function_entry()
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

def atualizar_df_games(new_game_data):
    log_function_entry()
    global df_games
    df_games = pd.concat([df_games, pd.DataFrame([new_game_data])], ignore_index=True)

def remover_df_games(matches_to_remove, simulador=True):
    log_function_entry()
    # Obter os índices dos jogos a serem removidos
    indices_to_remove = matches_to_remove.index

    # Remover os jogos do DataFrame original
    df_games.drop(indices_to_remove, inplace=True)

### Dicionário de correção
def verificar_listagem(set_output, set_default):
    log_function_entry()
    elementos_ausentes = set(set_output) - set(set_default)
    if len(elementos_ausentes) > 0:
        logging.critical("Os seguintes elementos não estão listados:")
        logging.critical(elementos_ausentes)

def corrigir_local(df_games):
    log_function_entry()
    locations = ['Palestra', 'USCS', 'Idalina', 'Pinheiros', 'SEMEF', 'GETA', 'EDA', 'CESPRO', 'Mané Garrincha', 'Mauro Pinheiro', 'Baby Barione', 'CERET', 'Mauro Pinheiro']
    correction_local = {
        'Pale stra': 'Palestra',
        'Idal ina': 'Idalina',
        'SEM EF': 'SEMEF',
        'GE TA': 'GETA',
        'Mané Ga rrincha': 'Mané Garrincha',
        'US CS': 'USCS',
        'Baby B arione' : 'Baby Barione',
        'CER ET' : 'CERET',
        'Mauro P inheiro' : 'Mauro Pinheiro',
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
    log_function_entry()
    teams = []
    for col in tb_group.columns:
        teams += tb_group[col].dropna().tolist()

    correction_teams = {
        'ArquiteturaMackenzie': 'Arquitetura Mackenzie',
        'Belas A rtes': 'Belas Artes',
        'BelasArtes': 'Belas Artes',
        'CAAP U FABC': 'CAAP UFABC',
        'CásperLíbero': 'Cásper Líbero',
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
        'Direito U NICID': 'Direito UNICID',
        'DireitoFMU': 'Direito FMU',
        'EACHUSP': 'EACH USP',
        'ECA U SP': 'ECA USP',
        'Economia M ackenzie': 'Economia Mackenzie',
        'Economia M ackenzie': 'Economia Mackenzie',
        'Educação Fís i ca Anhembi': 'Educação Física Anhembi',
        'Educação Fís i ca UNINOVE': 'Educação Física UNINOVE',
        'Educação Fís ica Anhembi': 'Educação Física Anhembi',
        'Educação Físi ca UNINOVE': 'Educação Física UNINOVE',
        'EEFEUSP': 'EEFE USP',
        'EngenhariaAnhembi': 'Engenharia Anhembi',
        'EngenhariaMackenzie': 'Engenharia Mackenzie',
        'EngenhariaSão Judas': 'Engenharia São Judas',
        'EngenhariaUNICAMP': 'Engenharia UNICAMP',
        'ESE G': 'ESEG',
        'ESP M': 'ESPM',
        'FA A P': 'FAAP',
        'FAA P': 'FAAP',
        'Farmác ia USP': 'Farmácia USP',
        'Fatec Sã o Paulo': 'Fatec São Paulo',
        'FATEC Sã o Paulo': 'FATEC São Paulo',
        'FAUUSP': 'FAU USP',
        'FE I': 'FEI',
        'FEA P UC': 'FEA PUC',
        'FEA São J udas***': 'FEA São Judas',
        'FEA SãoJudas': 'FEA São Judas',
        'FEA U SP': 'FEA USP',
        'FEC AP': 'FECAP',
        'Federaldo ABC': 'Federal do ABC',
        'FFLCHUSP': 'FFLCH USP',
        'FM U': 'FMU',
        'GetúlioVargas': 'Getúlio Vargas',
        'IBM EC': 'IBMEC',
        'IBME C SP': 'IBMEC SP',
        'IME U SP': 'IME USP',
        'INS P ER': 'INSPER',
        'INSP ER': 'INSPER',
        'IT A': 'ITA',
        'LEP Ma c kenzie': 'LEP Mackenzie',
        'LEP Mac kenzie': 'LEP Mackenzie',
        'LEP MAC KENZIE': 'LEP Mackenzie',
        'LinkSB': 'Link SB',
        'Ma uá': 'Mauá',
        'Medici n a ABC': 'Medicina ABC',
        'Medici n a USP': 'Medicina USP',
        'Medicin a ABC': 'Medicina ABC',
        'Medicin a ABC': 'Medicina ABC',
        'Medicin a Mauá': 'Medicina Mauá',
        'Medicin a Mogi': 'Medicina Mogi',
        'Medicin a Santos': 'Medicina Santos',
        'Medicin a USP': 'Medicina USP',
        'Medicina B ela Vista': 'Medicina Bela Vista',
        'Medicina PU C Campinas': 'Medicina PUC Campinas',
        'Medicina S ã o Caetano': 'Medicina São Caetano',
        'Medicina S anta Casa': 'Medicina Santa Casa',
        'Medicina S ão Camilo': 'Medicina São Camilo',
        'Medicina S �o Camilo': 'Medicina São Camilo',
        'Medicina Sa nto Amaro': 'Medicina Santo Amaro',
        'Medicina Sã o Bernardo': 'Medicina São Bernardo',
        'Medicina Sã o Caetano': 'Medicina São Caetano',
        'Medicina San  ta Marcelina': 'Medicina Santa Marcelina',
        'Medicina San ta Marcelina': 'Medicina Santa Marcelina',
        'Medicina S�o Caetano': 'Medicina São Caetano',
        'Medicina Ta ubaté (DT)': 'Medicina Taubaté',
        'Medicina U NICAMP': 'Medicina UNICAMP',
        'Medicina U NINOVE': 'Medicina UNINOVE',
        'Medicina UN E SP Botucatu': 'Medicina UNESP Botucatu',
        'Medicina UNE SP Botucatu': 'Medicina UNESP Botucatu',
        'MedicinaAnhembi': 'Medicina Anhembi',
        'MedicinaBragança': 'Medicina Bragança',
        'MedicinaEinstein': 'Medicina Einstein',
        'MedicinaJundiaí': 'Medicina Jundiaí',
        'MedicinaMANDIC': 'Medicina MANDIC',
        'MedicinaOsasco': 'Medicina Osasco',
        'MedicinaPaulista': 'Medicina Paulista',
        'MedicinaTaubaté': 'Medicina Taubaté',
        'MedicinaUNICID': 'Medicina UNICID',
        'MedicinaUNIMES': 'Medicina UNIMES',
        'MedicinaZ Taubaté': 'Medicina Taubaté',
        'Odontologi a UNINOVE': 'Odontologia UNINOVE',
        'Politécn ica USP': 'Politécnica USP',
        'Psicolog ia PUC': 'Psicologia PUC',
        'Psicologia  d a PUC SP': 'Psicologia da PUC SP',
        'Psicologia d a PUC SP': 'Psicologia da PUC SP',
        'RI P UC': 'RI PUC',
        'SEN  AC': 'SENAC',
        'SEN AC': 'SENAC',
        'SENAC (WO)': 'SENAC',
        'Sistema de Inf ormação USP': 'Sistema de Informação USP',
        'Stron g BS': 'Strong BS',
        'TecnologiaMackenzie': 'Tecnologia Mackenzie',
        'UN IP': 'UNIP',
        'UNIFESP D iadema': 'UNIFESP Diadema',
        'Unifesp S ão Paulo': 'Unifesp São Paulo',
        'UNIFESP S ão Paulo': 'UNIFESP São Paulo',
        'UNIFESPOsasco': 'UNIFESP Osasco',
        'US C S': 'USCS',
        'US CS': 'USCS',
        'USCS (WO)': 'USCS',
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
    log_function_entry()
    # Salvar a coluna 'ID' em uma variável temporária
    id_column = df_original.pop('ID')

    # Redefinir o índice do DataFrame df_original
    df_original.reset_index(inplace=True)

    # Atualizar os dados em df_original com base em df_nova
    for index, row in df_nova.iterrows():
        log_function_entry()
        time = row['Time']
        idx = df_original[df_original['Time'] == time].index
        if not idx.empty:
            df_original.loc[idx[0]] = row

    # Reatribuir a coluna 'ID' ao DataFrame df_original
    df_original['ID'] = id_column

    # Agora, df_original contém os dados atualizados
    return df_original

def get_rankings_zero_group(modality):
    log_function_entry()
    ranking_A = load_json_data(f'files/{modality}/group/ranking_zero_A.json')
    ranking_B = load_json_data(f'files/{modality}/group/ranking_zero_B.json')
    return {
        'A': ranking_A,
        'B': ranking_B
    }

def get_index_teams(rankings):
    log_function_entry()
    ranking_dict_A = {time_dict['Time']: index for index, time_dict in enumerate(rankings['A'])}
    ranking_dict_B = {time_dict['Time']: index for index, time_dict in enumerate(rankings['B'])}
    return {
        'A': ranking_dict_A,
        'B': ranking_dict_B
    }

def generate_ranking_by_games(modality):
    log_function_entry()
    
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
    log_function_entry()
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
                        logging.info(f"Classificação grupo {chr(idx + 64)} atualizada com confrontos diretos:")
                        logging.info(f'Por confronto direto: 1º {team_ahead} 2º {team_behind}')
                
        df_groups.append(df_group)
        idx = idx + 1
    return df_groups

def format_tb_group(tb_group):
    log_function_entry()
    if list(tb_group.columns) != ['Grupo A', 'Grupo B']:
        # Definir a primeira linha como cabeçalho da tabela
        tb_group.columns = tb_group.iloc[0]
        # Remover a primeira linha, que agora é o cabeçalho
        return tb_group[1:]
    return tb_group
    
def update_game(modality, game_id, home_goal, away_goal):
    log_function_entry()
    file_path = f'files/{modality}/games.json'
    games_data = load_json_data(file_path)

    # Encontrar o jogo com o ID fornecido
    for game in games_data:
        if game['ID'] == game_id:
            # Atualizar o placar, gols do mandante e gols do visitante
            group = game['GRUPO']
            game['PLACAR'] = f"{home_goal}X{away_goal}"
            game['GOLS_MANDANTE'] = str(home_goal)
            game['GOLS_VISITANTE'] = str(away_goal)
            home_team = game['Mandante'] 
            away_team = game['Visitante']
            winner_team = home_team
            loser_team = away_team
            draw = False
            if int(home_goal) < int(away_goal):
                log_function_entry()
                winner_team = away_team
                loser_team = home_team
            elif home_goal == away_goal: 
                draw = True
            break
    
    file_path_group = f'files/{modality}/group'
    save_json_data(games_data, file_path)
    confrontos_diretos = load_json_data(f'files/{modality}/confrontation.json')
    df_confrontos_diretos = confrontos_to_df(update_confronto_direto(winner_team, loser_team, draw, confrontos_diretos))
    rankings = generate_ranking_by_games(modality)
    df_groups = update_ranking([rankings[group]], df_confrontos_diretos)

    df_group = df_groups[0]
    df_group.to_csv(f'{file_path_group}/ranking_{group}.csv', index=False)

    csv_to_json(f'{file_path_group}/ranking_{group}.csv', f'{file_path_group}/ranking_{group}.json') 

def format_DIA_HORARIO(games_data):
    log_function_entry()
    if 'DIA HORÁRIO' in games_data.columns:
        current_year = datetime.datetime.now().year

        def process_date_time(value):
            if value.strip() != "":
                value_strip = value[:6].strip()
                value_fmt = value_strip.replace(" ", "")
                value_with_year = f"{value_fmt}/{current_year}"
                date = pd.to_datetime(value_with_year, format='%d/%m/%Y', errors='coerce').date()
                time = value.replace(value_strip, '').strip().replace(" ", "")
                return date, time
            else:
                return pd.NaT, ''

        # Aplicar a função à coluna "DIA HORÁRIO" apenas se o campo 'DIA' não for NaT e o campo 'HORARIO' não for NaN
        games_data[['DIA', 'HORARIO']] = games_data.apply(lambda row: process_date_time(row['DIA HORÁRIO']) if pd.isna(row['DIA']) and pd.isna(row['HORARIO']) else (row['DIA'], row['HORARIO']), axis=1).apply(pd.Series)
        games_data.drop(columns=['DIA HORÁRIO'], inplace=True)

    return games_data

def format_LOCAL_GRUPO(games_data):
    log_function_entry()
    if 'LOCAL GRUPO' in games_data.columns:

        def process_date_time(value):
            if value.strip() != "":
                value_strip = value[:-1].strip()  # Remove o último caractere
                local = value_strip.strip()  # Aplica trim ao local
                group = value[-1]  # Último caractere como group
                return local, group
            else:
                return pd.NaT, pd.NaT

        # Aplicar a função à coluna "DIA HORÁRIO" apenas se o campo 'DIA' não for NaT e o campo 'HORARIO' não for NaN
        games_data[['LOCAL', 'GRUPO']] = games_data.apply(lambda row: process_date_time(row['LOCAL GRUPO']) if pd.isna(row['LOCAL']) and pd.isna(row['GRUPO']) else (row['LOCAL'], row['GRUPO']), axis=1).apply(pd.Series)
        games_data.drop(columns=['LOCAL GRUPO'], inplace=True)

    return games_data

def execute_zero_ranking(dic_modalities_page):
    log_function_entry()
    for key, value in dic_modalities_page.items():
        logging.info(f"modalidade: {key}")
        modality = key
        # tables = tabula.read_pdf("files/Boletim.pdf", pages=dic_modalities_page[modality])
        tables = tabula.read_pdf("files/Boletim.pdf", pages=value)
        tb_group = format_tb_group(tables[0])
        tb_games = [tables[1], tables[2]]

        filepath = 'files/' + modality
        filepath_group = filepath + '/group'
        create_zero_ranking_group(tb_group, filepath_group)
        df_games = generate_table_games(tb_games)
        df_games = corrigir_local(df_games)
        df_games = corrigir_times(tb_group, df_games)
        create_files(df_games, filepath)
        gerar_confronto_direto(df_games, filepath)

def check_game_data(modality, filaname='games'):
    log_function_entry()
    file_path = f'files/{modality}/{filaname}.json'
    json_data = load_json_data(file_path)
    
    # Verifica o formato dos campos 'DIA' e 'HORARIO' para cada jogo
    for json_game in json_data:
        if len(str(json_game['DIA'])) != 10:
            logging.critical(f"Jogo {json_game['ID']} com DIA inválido: {json_game['DIA']}")
        if len(str(json_game['HORARIO'])) > 8:
            logging.critical(f"Jogo {json_game['ID']} com HORARIO inválido: {json_game['HORARIO']}")
    
def corrigir_horario(df):
    log_function_entry()
    # Corrigir o campo 'HORARIO' para cada jogo no DataFrame
    for index, row in df.iterrows():
        horario = str(row['HORARIO']).replace(" ", "")  # Remover espaços em branco
        horario = horario[-8:]  # Pegar os últimos 8 caracteres
        df.at[index, 'HORARIO'] = horario  # Atualizar o valor do campo 'HORARIO'
    
    return df

def corrigir_dia(games_data):
    log_function_entry()
    # Corrigir a coluna 'DIA' se estiver no formato de data e hora completa
    games_data['DIA'] = games_data['DIA'].apply(lambda x: str(x)[:10] if pd.notnull(x) else x)
    
    return games_data

def preencher_simulador(df):
    log_function_entry()
    for index, row in df.iterrows():
        dia_jogo = pd.to_datetime(row['DIA'], format='%Y-%m-%d', errors='coerce').date()
        if pd.isna(dia_jogo) or dia_jogo > dia_atual or row['PLACAR'] == 'X':
            df.at[index, 'PLACAR'] = 'X'
            df.at[index, 'GOLS_MANDANTE'] = ''
            df.at[index, 'GOLS_VISITANTE'] = ''
            df.at[index, 'SIMULADOR'] = True
    
    return df

def corrigir_label(df_games): 
    log_function_entry()
    """Corrige os rótulos das equipes."""
    correction_label = {
        'Vencedor d as 4as (4)': 'Vencedor das 4as (4)',
        'Vencedor d as 4as (3)': 'Vencedor das 4as (3)',
        'Vencedor d as 4as (2)': 'Vencedor das 4as (2)',
        'Vencedor d as 4as (1)': 'Vencedor das 4as (1)',
    }
    # Função de validação e correção
    def correct_label(label):
        return correction_label.get(label.strip(), label.strip())

    df_games['label Mandante'] = df_games['label Mandante'].apply(correct_label)
    df_games['label Visitante'] = df_games['label Visitante'].apply(correct_label)
    return df_games

def corrigir_fase(df_games): 
    log_function_entry()
    """Corrige as fases dos jogos."""
    correction_label = {
        '4a s (1)': '4as (1)',
        '4a s (2)': '4as (2)',
        '4a s (3)': '4as (3)',
        '4a s (4)': '4as (4)',
        'Sem i (1)': 'Semi (1)',
        'Sem i (2)': 'Semi (2)',
    }
    # Função de validação e correção
    def correct_fase(label):
        return correction_label.get(label.strip(), label.strip())

    df_games['FASE'] = df_games['FASE'].apply(correct_fase)
    return df_games

def generate_playoff_games(tables):
    """Gera uma tabela de jogos a partir dos dados fornecidos."""
    
    df = pd.DataFrame(tables)

    if 'FASE EQUIPE Mandante' in df.columns:
        df = split_fase_equipe(df)
    # Lista para armazenar as novas linhas
    new_rows = []

    # Iterar sobre o DataFrame em blocos de 3 linhas
    for i in range(0, len(df), 3):
        row1 = df.iloc[i]
        row2 = df.iloc[i+1]
        row3 = df.iloc[i+2]
        
        # Criar uma nova linha combinando as colunas especificadas
        new_row = {
            'FASE': (row1['FASE'] if pd.notna(row1['FASE']) else '') + ' ' + (row3['FASE'] if pd.notna(row3['FASE']) else ''),
            'label Mandante': (row1['EQUIPE Mandante'].strip() if pd.notna(row1['EQUIPE Mandante']) else ''),
            'label Visitante': (row1['EQUIPE Visitante'].strip() if pd.notna(row1['EQUIPE Visitante']) else ''),
            'EQUIPE Mandante': (row3['EQUIPE Mandante'] if pd.notna(row3['EQUIPE Mandante']) else ''),
            'EQUIPE Visitante': (row3['EQUIPE Visitante'] if pd.notna(row3['EQUIPE Visitante']) else ''),
            'DIA': row2['DIA'] if pd.notna(row2['DIA']) else '',
            'HORARIO': row2['HORÁRIO'] if pd.notna(row2['HORÁRIO']) else '',
            'LOCAL': row2['LOCAL'] if pd.notna(row2['LOCAL']) else '',
            'PLACAR': row2['PLACAR'] if pd.notna(row2['PLACAR']) else ''
        }

        new_row['SIMULADOR'] = False
        
        # Adicionar a nova linha à lista
        new_rows.append(new_row)

    # Atualizar as colunas do DataFrame com as novas linhas
    df_games = pd.DataFrame(new_rows)
    df_games['ID'] = [generate_game_id() for _ in range(len(df_games))]
    df_games.rename(columns={'HORÁRIO': 'HORARIO', 'EQUIPE Mandante': 'Mandante', 'EQUIPE Visitante': 'Visitante'}, inplace=True)
    df_games[['GOLS_MANDANTE', 'GOLS_VISITANTE']] = df_games['PLACAR'].str.split('X', expand=True)
    return df_games

def execute_update_data_playoff_by_modality(modality, page):

    logging.info(f"**** update_data_playoff_by_modality ****")
    logging.info(f"modalidade: {modality}")
    tables = tabula.read_pdf("files/Boletim.pdf", pages=page)

    filepath = f'files/{modality}'
    df_games_playoff = generate_playoff_games(tables[0])
    df_games_playoff = corrigir_label(df_games_playoff)
    df_games_playoff = corrigir_fase(df_games_playoff)
    # df_games_playoff = corrigir_times(df_games_playoff)
    df_games_playoff = corrigir_local(df_games_playoff)
    df_games_playoff = corrigir_horario(df_games_playoff)
    df_games_playoff = corrigir_dia(df_games_playoff)
    create_files(df_games_playoff, filepath, 'playoff')
    check_game_data(modality, 'playoff')

def execute_update_data_by_modality(modality, pages):
    log_function_entry()
    logging.info(f"**** execute_update_data_by_modality ****")
    logging.info(f"modalidade: {modality}")
    tables = tabula.read_pdf("files/Boletim.pdf", pages=pages)
    tb_group = format_tb_group(tables[0])
    tb_games = [tables[1], tables[2]]

    filepath = f'files/{modality}'
    df_games = generate_table_games(tb_games)
    
    df_games = corrigir_times(tb_group, df_games)

    # if modality == 'FM/F':
    #     df_games = format_DIA_HORARIO(df_games)

    # if modality == 'FM/B':
    #     df_games = format_LOCAL_GRUPO(df_games)

    df_games = corrigir_local(df_games)
    df_games = corrigir_horario(df_games)
    df_games = corrigir_dia(df_games)
    df_games = preencher_simulador(df_games)
    create_files(df_games, filepath)
    
    confrontos = gerar_confronto_direto(df_games, filepath)
    df_confrontos_diretos = confrontos_to_df(confrontos)
    rankings = generate_ranking_by_games(modality)
    df_groups = update_ranking([rankings['A'], rankings['B']], df_confrontos_diretos)
    df_groupA = df_groups[0]
    df_groupB = df_groups[1]

    df_groupA.to_csv(f'files/{modality}/group/ranking_A.csv', index=False)
    df_groupB.to_csv(f'files/{modality}/group/ranking_B.csv', index=False)

    csv_to_json(f'files/{modality}/group/ranking_A.csv', f'files/{modality}/group/ranking_A.json')
    csv_to_json(f'files/{modality}/group/ranking_B.csv', f'files/{modality}/group/ranking_B.json')
    check_game_data(modality)

def execute_update_data(dic_modalities_page):
    log_function_entry()
    for key, value in dic_modalities_page.items():
        execute_update_data_by_modality(key, value)
        logging.info("----------------------------------------")

def execute_update_data_playoff(dic_modalities_page):

    for key, value in dic_modalities_page.items():
        execute_update_data_playoff_by_modality(key, value)
        logging.info("----------------------------------------")

def update_ranking_by_games(modality):
    log_function_entry()
    filepath = f'files/{modality}'
    df_games = pd.read_json(f'{filepath}/games.json')

    confrontos = gerar_confronto_direto(df_games, filepath)
    df_confrontos_diretos = confrontos_to_df(confrontos)
    rankings = generate_ranking_by_games(modality)
    df_groups = update_ranking([rankings['A'], rankings['B']], df_confrontos_diretos)
    df_groupA = df_groups[0]
    df_groupB = df_groups[1]

    df_groupA.to_csv(f'files/{modality}/group/ranking_A.csv', index=False)
    df_groupB.to_csv(f'files/{modality}/group/ranking_B.csv', index=False)

    csv_to_json(f'files/{modality}/group/ranking_A.csv', f'files/{modality}/group/ranking_A.json')
    csv_to_json(f'files/{modality}/group/ranking_B.csv', f'files/{modality}/group/ranking_B.json')  

def generate_dic_modalities_page(first_page, modalities):
    log_function_entry()
    # Inicializa o dicionário vazio
    dic_modalities_page = {}

    # Define a quantidade de páginas por modalidade
    pages_per_modality = 2

    # Define o intervalo entre as modalidades
    interval_between_modalities = 2

    # Preenche o dicionário com as modalidades fornecidas
    for i, modality in enumerate(modalities):
        start_page = first_page + i * (pages_per_modality + interval_between_modalities)
        end_page = start_page + pages_per_modality - 1
        dic_modalities_page[modality] = f"{start_page}-{end_page}"

    # Imprime o dicionário resultante
    logging.info("dic_modalities_page")
    logging.info(dic_modalities_page)
    return dic_modalities_page

# Lista das modalidades
modalities = [
    "FF/A", "FF/B", "FF/C", "FF/D", "FF/E",
    "FM/A", "FM/B", "FM/C", "FM/D", "FM/E", "FM/F" 
]

dic_modalities_page = generate_dic_modalities_page(48, modalities)

execute_zero_ranking(dic_modalities_page)

# dic_modalities_page = {
# #         "FF/A" : "48-49",
# #         "FF/B" : "50-51",
# #         "FF/C" : "53-54",
#         # "FF/D" : "60-61",
#         "FF/E" : "64-65",
# #         "FM/A" : "65-66",
# #         "FM/B" : "69-70",
# #         "FM/C" : "73-74",
# #         "FM/E" : "81-82",
# #         "FM/F" : "85-86",
# #         "FM/D" : "77-78",
#     }


# dic_modalities_page_playoff = {
#         # "FF/A" : "48",
#         # "FF/B" : "52",
#         "FF/C" : "56",
#         # "FF/D" : "60",
#         "FF/E" : "64",
#         # "FM/A" : "68",
#         "FM/B" : "72",
#         # "FM/C" : "76",
#         "FM/D" : "80",
#         "FM/E" : "84",
#         # "FM/F" : "88",
#     }

# execute_update_data(dic_modalities_page)
# execute_update_data_playoff(dic_modalities_page_playoff)
# execute_update_data_by_modality("FM/F", "84-85")
# execute_update_data_by_modality("FM/D", "76-77")
# update_ranking_by_games("FM/F")