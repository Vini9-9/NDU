import tabula
import pandas as pd
import uuid
import csv
import json
import os
import datetime
import logging
import inspect
import zipfile

data_hora_atual = datetime.datetime.now()

dia_atual = data_hora_atual.date()

logging.basicConfig(filename='logs/debug_ndu_' + data_hora_atual.strftime("%Y-%m-%d_%H-%M-%S") + '.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

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
    json_file = f"{full_filepath}.json"
    create_json_from_df(df_games, json_file)

def create_backup_zipped(source_folder='files', backup_folder='backup'):
    # Certifique-se de que o diretório de backup existe
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)

    # Obter a data e hora atuais
    data_hora_atual = datetime.datetime.now()
    timestamp = data_hora_atual.strftime("%Y-%m-%d_%H-%M-%S")

    # Criar o nome do arquivo zip
    zip_filename = f"backup_{timestamp}.zip"
    zip_filepath = os.path.join(backup_folder, zip_filename)

    # Criar o arquivo zip
    with zipfile.ZipFile(zip_filepath, 'w') as zipf:
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                file_path = os.path.join(root, file)
                # Adicionar o arquivo ao zip
                zipf.write(file_path, os.path.relpath(file_path, source_folder))

    logging.info(f"Arquivo zip criado: {zip_filepath}")