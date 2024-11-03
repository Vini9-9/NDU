from check import check_game_data
from fixes import corrigir_dia, corrigir_horario, corrigir_local
from utils import create_files, log_function_entry, generate_game_id
import logging
import tabula
import pandas as pd


def split_fase_equipe(df):
    """Divide a coluna 'FASE EQUIPE Mandante' em 'FASE' e 'EQUIPE Mandante'."""
    df['FASE'] = df['FASE EQUIPE Mandante'].apply(lambda x: x[:-24] if len(x) > 24 else '')
    df['EQUIPE Mandante'] = df['FASE EQUIPE Mandante'].apply(lambda x: x[-24:] if len(x) > 24 else x)
    return df

def generate_playoff_games(tables):
    
    df = pd.DataFrame(tables)
    
    # Lista para armazenar as novas linhas
    new_rows = []

    # Iterar sobre o DataFrame em blocos de 3 linhas
    for i in range(0, len(df) - 2, 3):
        row1 = df.iloc[i]
        row2 = df.iloc[i+1]
        row3 = df.iloc[i+2]
        
        # Criar uma nova linha combinando as informações
        new_row = {
            'FASE': ' '.join(filter(None, [str(row1['FASE']), str(row3['FASE'])])),
            'label Mandante': str(row1['EQUIPE Mandante']).strip(),
            'label Visitante': str(row1['EQUIPE Visitante']).strip(),
            'EQUIPE Mandante': str(row3['EQUIPE Mandante']).strip(),
            'EQUIPE Visitante': str(row3['EQUIPE Visitante']).strip(),
            'DIA': str(row2['DIA']),
            'HORARIO': str(row2['HORÁRIO']),
            'LOCAL': str(row2['LOCAL']),
            'PLACAR': str(row2['PLACAR'])
        }

        new_row['SIMULADOR'] = False
        
        # Adicionar a nova linha à lista apenas se tiver informações relevantes
        if any(value.strip() for value in new_row.values() if isinstance(value, str)):
            new_rows.append(new_row)

    # Criar um novo DataFrame com as linhas processadas
    result_df = pd.DataFrame(new_rows)
    result_df['ID'] = [generate_game_id() for _ in range(len(result_df))]
    result_df.rename(columns={'HORÁRIO': 'HORARIO', 'EQUIPE Mandante': 'Mandante', 'EQUIPE Visitante': 'Visitante'}, inplace=True)
    result_df[['GOLS_MANDANTE', 'GOLS_VISITANTE']] = result_df['PLACAR'].str.split('X', expand=True)
    
    # Substituir 'nan' por string vazia
    result_df = result_df.replace('nan', '', regex=True)
    
    return result_df


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

def execute_update_data_playoff_by_modality(modality, page):
    log_function_entry()
    logging.info(f"Modalidade: {modality}")
    tables = tabula.read_pdf("files/Boletim.pdf", pages=page)

    filepath = f'files/{modality}'
    df_games_playoff = generate_playoff_games(tables[0])
    df_games_playoff = corrigir_label(df_games_playoff)
    df_games_playoff = corrigir_fase(df_games_playoff)
    df_games_playoff = corrigir_local(df_games_playoff)
    df_games_playoff = corrigir_horario(df_games_playoff)
    df_games_playoff = corrigir_dia(df_games_playoff)
    create_files(df_games_playoff, filepath, 'playoff')
    check_game_data(modality, 'playoff')

def execute_update_data_playoff(dic_modalities_page):

    for key, value in dic_modalities_page.items():
        execute_update_data_playoff_by_modality(key, value)
        logging.info("----------------------------------------")

dic_modalities_page_playoff = {
        "FF/A" : "51",
        "FF/B" : "55",
        "FF/C" : "59",
        "FF/D" : "63",
        "FF/E" : "68",
        "FM/A" : "72",
        "FM/B" : "76",
        "FM/C" : "80",
        "FM/D" : "84",
        "FM/E" : "88",
        "FM/F" : "93",
    }

execute_update_data_playoff(dic_modalities_page_playoff)