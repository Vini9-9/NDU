import logging

import pandas as pd
from utils import log_function_entry

LOCATIONS = {
    'Mackenzie', 'SENAC', 'Medicina USP', 'Palestra', 'USCS', 'Idalina', 'Pinheiros', 
    'SEMEF', 'GETA', 'EDA', 'CESPRO', 'Mané Garrincha', 'Mauro Pinheiro', 'Baby Barione', 'CERET'
}

def format_tb_group(tb_group_array):
    log_function_entry()
    for tb_group in tb_group_array:
        header_zero = tb_group.columns[0]
        if 'futsal' in header_zero.lower():
                logging.info(f"Tabela de Futsal encontrada. Passando para a próxima tabela.")
                continue
        
        if 'grupo' not in header_zero.lower():
            print('tb_group')
            print(tb_group)
            logging.warning(f"header_zero inválido: {header_zero}")
            logging.info(f"Colocando o header atual na última linha")
            # Adicionar os cabeçalhos atuais à última linha de valores de cada coluna
            tb_group.loc[len(tb_group)+1] = tb_group.columns

            num_cols = tb_group.shape[1]
            new_headers = [f'Grupo {chr(65 + i)}' for i in range(num_cols)]

            logging.info(f"Atualizando headers")
            # Atualizar os cabeçalhos do DataFrame
            tb_group.columns = new_headers
        return tb_group

def verificar_listagem(set_output, set_default):
    log_function_entry()
    elementos_ausentes = set(set_output) - set(set_default)
    if len(elementos_ausentes) > 0:
        logging.critical("Os seguintes elementos não estão listados:")
        logging.critical(elementos_ausentes)

# def corrigir_local(df_games):
#     log_function_entry()
#     locations = [
#         'Mackenzie', 
#         'SENAC', 
#         'Medicina USP', 
#         'Palestra', 
#         'USCS', 
#         'Idalina', 
#         'Pinheiros', 
#         'SEMEF', 
#         'GETA', 
#         'EDA', 
#         'CESPRO', 
#         'Mané Garrincha', 
#         'Mauro Pinheiro', 
#         'Baby Barione',
#         'CERET'
#         ]
#     correction_local = {
#         'Pale stra': 'Palestra',
#         'Idal ina': 'Idalina',
#         'SEM EF': 'SEMEF',
#         'GE TA': 'GETA',
#         'Mané Ga rrincha': 'Mané Garrincha',
#         'US CS': 'USCS',
#         'Baby B arione' : 'Baby Barione',
#         'Baby B arioni' : 'Baby Barione',
#         'SEN AC' : 'SENAC',
#         'CER ET' : 'CERET',
#         'Mack enzie' : 'Mackenzie',
#         'Mauro P inheiro' : 'Mauro Pinheiro',
#         'Medicin a USP' : 'Medicina USP',
#         'CDC Ip asure': 'CDC Ipasure',
#         'APC EF': 'APCEF',
#     }
#     # Função de validação e correção
#     def correct_local(local):
#         if local in locations:
#             return local
#         elif local in correction_local:
#             return correction_local[local]
#         else:
#             return local

#     # Aplicar a função de validação e correção nas colunas 'EQUIPE Mandante' e 'EQUIPE Visitante'
#     df_games['LOCAL'] = df_games['LOCAL'].apply(correct_local)
#     verificar_listagem(df_games['LOCAL'].unique(), locations)
#     return df_games

from functools import lru_cache

@lru_cache(maxsize=None)
def correct_local(local):
    correction_local = {
        'Pale stra': 'Palestra',
        'Idal ina': 'Idalina',
        'SEM EF': 'SEMEF',
        'GE TA': 'GETA',
        'Mané Ga rrincha': 'Mané Garrincha',
        'US CS': 'USCS',
        'Baby B arione': 'Baby Barione',
        'Baby B arioni': 'Baby Barione',
        'SEN AC': 'SENAC',
        'CER ET': 'CERET',
        'Mack enzie': 'Mackenzie',
        'Mauro P inheiro': 'Mauro Pinheiro',
        'Medicin a USP': 'Medicina USP',
        'CDC Ip asure': 'CDC Ipasure',
        'APC EF': 'APCEF',
    }
    return local if local in LOCATIONS else correction_local.get(local, local)

def verificar_listagem(set_output, set_default):
    logging.info("Iniciando verificação de listagem")
    elementos_ausentes = set(set_output) - set(set_default)
    if len(elementos_ausentes) > 0:
        logging.critical("Os seguintes elementos não estão listados:")
        logging.critical(elementos_ausentes)

def corrigir_local(df_games):
    logging.info("Iniciando correção de locais")
    df_games['LOCAL'] = df_games['LOCAL'].map(correct_local)
    verificar_listagem(df_games['LOCAL'].unique(), LOCATIONS)
    return df_games

# def corrigir_times(teams, df_games):
#     log_function_entry()

#     correction_teams = {
#         'ArquiteturaMackenzie': 'Arquitetura Mackenzie',
#         'Belas A rtes': 'Belas Artes',
#         'BelasArtes': 'Belas Artes',
#         'CAAP U FABC': 'CAAP UFABC',
#         'CásperLíbero': 'Cásper Líbero',
#         'Comunica ção PUC': 'Comunicação PUC',
#         'Comunicaçã o Anhembi': 'Comunicação Anhembi',
#         'Comunicação Anhembi (DT)': 'Comunicação Anhembi',
#         'Comunicação A nhembi (WO)': 'Comunicação Anhembi',
#         'Comunicaçã o Mackenzie': 'Comunicação Mackenzie',
#         'Comunicaçã o Metodista': 'Comunicação Metodista',
#         'Direit o PUC': 'Direito PUC',
#         'Direit o USP': 'Direito USP',
#         'Direito M ackenzie': 'Direito Mackenzie',
#         'Direito S ã o Judas': 'Direito São Judas',
#         'Direito S ão Judas': 'Direito São Judas',
#         'Direito SãoBernardo': 'Direito São Bernardo',
#         'Direito U NICID': 'Direito UNICID',
#         'DireitoFMU': 'Direito FMU',
#         'EACHUSP': 'EACH USP',
#         'ECA U SP': 'ECA USP',
#         'Economia M ackenzie': 'Economia Mackenzie',
#         'Economia M ackenzie': 'Economia Mackenzie',
#         'Educação Fís i ca Anhembi': 'Educação Física Anhembi',
#         'Educação Fís i ca UNINOVE': 'Educação Física UNINOVE',
#         'Educação Fís ica Anhembi': 'Educação Física Anhembi',
#         'Educação Físi ca UNINOVE': 'Educação Física UNINOVE',
#         'EEFEUSP': 'EEFE USP',
#         'EngenhariaAnhembi': 'Engenharia Anhembi',
#         'EngenhariaMackenzie': 'Engenharia Mackenzie',
#         'EngenhariaSão Judas': 'Engenharia São Judas',
#         'EngenhariaUNICAMP': 'Engenharia UNICAMP',
#         'ESE G': 'ESEG',
#         'ES E G': 'ESEG',
#         'ESP M': 'ESPM',
#         'FA A P': 'FAAP',
#         'FAA P': 'FAAP',
#         'Farmác ia USP': 'Farmácia USP',
#         'Fatec Sã o Paulo': 'Fatec São Paulo',
#         'FATEC Sã o Paulo': 'FATEC São Paulo',
#         'FAUUSP': 'FAU USP',
#         'FE I': 'FEI',
#         'FEA P UC': 'FEA PUC',
#         'FEA São J udas***': 'FEA São Judas',
#         'FEA SãoJudas': 'FEA São Judas',
#         'FEA U SP': 'FEA USP',
#         'FEC AP': 'FECAP',
#         'Federaldo ABC': 'Federal do ABC',
#         'FFLCHUSP': 'FFLCH USP',
#         'FM U': 'FMU',
#         'FMU (DT)': 'FMU',
#         'GetúlioVargas': 'Getúlio Vargas',
#         'IBM EC': 'IBMEC',
#         'IBME C SP': 'IBMEC SP',
#         'ICBI�USP': 'ICBIÓ USP',
#         'IME U SP': 'IME USP',
#         'INS P ER': 'INSPER',
#         'INSP ER': 'INSPER',
#         'INSPER (DT)': 'INSPER',
#         'IT A': 'ITA',
#         'LEP Ma c kenzie': 'LEP Mackenzie',
#         'LEP Mac kenzie': 'LEP Mackenzie',
#         'LEP MAC KENZIE': 'LEP Mackenzie',
#         'LinkSB': 'Link SB',
#         'Ma uá': 'Mauá',
#         'Medici n a ABC': 'Medicina ABC',
#         'Medici n a USP': 'Medicina USP',
#         'Medicin a ABC': 'Medicina ABC',
#         'Medicin a Mauá': 'Medicina Mauá',
#         'Medicin a Mogi': 'Medicina Mogi',
#         'Medicin a Santos': 'Medicina Santos',
#         'Medicin a USP': 'Medicina USP',
#         'Medicina B ela Vista': 'Medicina Bela Vista',
#         'Medicina PU C Campinas': 'Medicina PUC Campinas',
#         'Medicina S ã o Caetano': 'Medicina São Caetano',
#         'Medicina S anta Casa': 'Medicina Santa Casa',
#         'Medicina S ão Camilo': 'Medicina São Camilo',
#         'Medicina S �o Camilo': 'Medicina São Camilo',
#         'Medicina Sa nto Amaro': 'Medicina Santo Amaro',
#         'Medicina Sã o Bernardo': 'Medicina São Bernardo',
#         'Medicina Sã o Caetano': 'Medicina São Caetano',
#         'Medicina San  ta Marcelina': 'Medicina Santa Marcelina',
#         'Medicina San ta Marcelina': 'Medicina Santa Marcelina',
#         'Medicina S�o Caetano': 'Medicina São Caetano',
#         'Medicina Ta ubaté (DT)': 'Medicina Taubaté',
#         'Medicina U NICAMP': 'Medicina UNICAMP',
#         'Medicina U NINOVE': 'Medicina UNINOVE',
#         'Medicina UN E SP Botucatu': 'Medicina UNESP Botucatu',
#         'Medicina UNE SP Botucatu': 'Medicina UNESP Botucatu',
#         'MedicinaAnhembi': 'Medicina Anhembi',
#         'MedicinaBragança': 'Medicina Bragança',
#         'MedicinaEinstein': 'Medicina Einstein',
#         'MedicinaJundiaí': 'Medicina Jundiaí',
#         'Medicin a JundiaÍ': 'Medicina Jundiaí',
#         'MedicinaMANDIC': 'Medicina MANDIC',
#         'MedicinaOsasco': 'Medicina Osasco',
#         'MedicinaPaulista': 'Medicina Paulista',
#         'Medicina PU C Sorocaba': 'Medicina PUC Sorocaba',
#         'MedicinaTaubaté': 'Medicina Taubaté',
#         'MedicinaUNICID': 'Medicina UNICID',
#         'MedicinaUNIMES': 'Medicina UNIMES',
#         'MedicinaZ Taubaté': 'Medicina Taubaté',
#         'Odontologi a UNINOVE': 'Odontologia UNINOVE',
#         'Politécn ica USP': 'Politécnica USP',
#         'Psicolog ia PUC': 'Psicologia PUC',
#         'Psicologia  d a PUC SP': 'Psicologia da PUC SP',
#         'Psicologia d a PUC SP': 'Psicologia da PUC SP',
#         'RI P UC': 'RI PUC',
#         'SEN  AC': 'SENAC',
#         'SEN AC': 'SENAC',
#         'SENAC (WO)': 'SENAC',
#         'SENAC (DT)': 'SENAC',
#         'Sistema de Inf ormação USP': 'Sistema de Informação USP',
#         'Stron g BS': 'Strong BS',
#         'TecnologiaMackenzie': 'Tecnologia Mackenzie',
#         'UN IP': 'UNIP',
#         'UNIFESP D iadema': 'UNIFESP Diadema',
#         'Unifesp S ão Paulo': 'Unifesp São Paulo',
#         'UNIFESP S ão Paulo': 'UNIFESP São Paulo',
#         'UNIFESPOsasco': 'UNIFESP Osasco',
#         'US C S': 'USCS',
#         'US CS': 'USCS',
#         'USCS (WO)': 'USCS',
#         'Veteriná ria USP': 'Veterinária USP',
#         'Zumbi dosPalmares': 'Zumbi dos Palmares',
#     }
#     # Função de validação e correção
#     def correct_team(equipe):
#         equipe_strip = equipe.strip().replace('  ', ' ')
#         if equipe_strip in teams:
#             return equipe_strip
#         elif equipe_strip in correction_teams:
#             return correction_teams[equipe_strip]
#         else:
#             return equipe_strip

#     # Aplicar a função de validação e correção nas colunas 'EQUIPE Mandante' e 'EQUIPE Visitante'
#     df_games['Mandante'] = df_games['Mandante'].apply(correct_team)
#     df_games['Visitante'] = df_games['Visitante'].apply(correct_team)
#     times_output = set(df_games['Mandante'].unique()) | set(df_games['Visitante'].unique())
#     verificar_listagem(times_output, teams)
#     return df_games

import pandas as pd
from fuzzywuzzy import process
import re

correct_teams = list(set(list(correction_teams.values())))

# Lista de palavras comuns em nomes de equipes
COMMON_WORDS = ['Comunicação', 'Direito', 'Engenharia', 'Medicina', 'Odontologia', 'Veterinária', 
                'Arquitetura', 'Economia', 'Psicologia', 'Farmácia', 'Educação', 'Física', 'Mackenzie',
                'UFABC', 'CAAP', 'Cásper', 'Líbero', 'Anhembi', 'USP', 'São', 'Bernardo', 
                'FMU', 'UNICAMP', 'ESEG', 'ESPM', 'FAAP', 'PUC', 'Palmares']

def preprocess_team_name(name):
    # Remover espaços extras e caracteres especiais
    name = re.sub(r'\s+', ' ', name)
    name = re.sub(r'[^\w\s]', '', name)
    return name.strip()

def find_best_match(name, correct_teams, threshold=80):
    # Primeiro, tenta encontrar uma correspondência exata
    if name in correct_teams:
        return name
    
    # Se não encontrar, usa a comparação fuzzy
    best_match = process.extractOne(name, correct_teams)
    if best_match and best_match[1] >= threshold:
        return best_match[0]
    
    # Se ainda não encontrou uma correspondência, retorna o nome original
    return name

def corrigir_times(correct_teams, df_games):
    correct_teams_set = set(correct_teams)
    
    def correct_team(name):
        name = preprocess_team_name(name)
        return find_best_match(name, correct_teams_set)
    
    df_games['Mandante'] = df_games['Mandante'].apply(correct_team)
    df_games['Visitante'] = df_games['Visitante'].apply(correct_team)
    
    return df_games

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