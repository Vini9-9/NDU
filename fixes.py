import logging

import pandas as pd
from utils import log_function_entry


def verificar_listagem(set_output, set_default):
    log_function_entry()
    elementos_ausentes = set(set_output) - set(set_default)
    if len(elementos_ausentes) > 0:
        logging.critical("Os seguintes elementos não estão listados:")
        logging.critical(elementos_ausentes)

def corrigir_local(df_games):
    log_function_entry()
    locations = [
        'Mackenzie', 
        'SENAC', 
        'Medicina USP', 
        'Palestra', 
        'USCS', 
        'Idalina', 
        'Pinheiros', 
        'SEMEF', 
        'GETA', 
        'EDA', 
        'CESPRO', 
        'Mané Garrincha', 
        'Mauro Pinheiro', 
        'Baby Barione',
        'CERET'
        ]
    correction_local = {
        'Pale stra': 'Palestra',
        'Idal ina': 'Idalina',
        'SEM EF': 'SEMEF',
        'GE TA': 'GETA',
        'Mané Ga rrincha': 'Mané Garrincha',
        'US CS': 'USCS',
        'Baby B arione' : 'Baby Barione',
        'Baby B arioni' : 'Baby Barione',
        'SEN AC' : 'SENAC',
        'CER ET' : 'CERET',
        'Mack enzie' : 'Mackenzie',
        'Mauro P inheiro' : 'Mauro Pinheiro',
        'Medicin a USP' : 'Medicina USP',
        'CDC Ip asure': 'CDC Ipasure',
        'APC EF': 'APCEF',
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

def corrigir_times(teams, df_games):
    log_function_entry()

    correction_teams = {
        'ArquiteturaMackenzie': 'Arquitetura Mackenzie',
        'Belas A rtes': 'Belas Artes',
        'BelasArtes': 'Belas Artes',
        'CAAP U FABC': 'CAAP UFABC',
        'CásperLíbero': 'Cásper Líbero',
        'Comunica ção PUC': 'Comunicação PUC',
        'Comunicaçã o Anhembi': 'Comunicação Anhembi',
        'Comunicação Anhembi (DT)': 'Comunicação Anhembi',
        'Comunicação A nhembi (WO)': 'Comunicação Anhembi',
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
        'FMU (DT)': 'FMU',
        'GetúlioVargas': 'Getúlio Vargas',
        'IBM EC': 'IBMEC',
        'IBME C SP': 'IBMEC SP',
        'IME U SP': 'IME USP',
        'INS P ER': 'INSPER',
        'INSP ER': 'INSPER',
        'INSPER (DT)': 'INSPER',
        'IT A': 'ITA',
        'LEP Ma c kenzie': 'LEP Mackenzie',
        'LEP Mac kenzie': 'LEP Mackenzie',
        'LEP MAC KENZIE': 'LEP Mackenzie',
        'LinkSB': 'Link SB',
        'Ma uá': 'Mauá',
        'Medici n a ABC': 'Medicina ABC',
        'Medici n a USP': 'Medicina USP',
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
        'SENAC (DT)': 'SENAC',
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