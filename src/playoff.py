import tabula
import pandas as pd
from utils import *
from ndu import *

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

# TODO - split_fase_equipe
def generate_playoff_games(tables):
    log_function_entry()
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
