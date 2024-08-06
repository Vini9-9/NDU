import firebase_admin
from firebase_admin import credentials, db, auth
import json
from dotenv import load_dotenv
import os
import datetime
import logging

data_hora_atual = datetime.datetime.now()

script_dir = os.path.dirname(os.path.realpath(__file__))
log_dir = os.path.join(script_dir, '..', 'logs')
env_dir = os.path.join(script_dir, '..', 'env')
files_dir = os.path.join(script_dir, '..', 'files')

# Configuração básica de logging
logging.basicConfig(filename=f'{log_dir}/log_db_modality_' + data_hora_atual.strftime("%Y-%m-%d_%H-%M-%S") + '.log', 
                    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

def get_json_data(json_file_path, group):
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = {
            "group": group,
            "ranking": json.load(file)
        }
        return data

def set_json_data(json_file_path, ref):
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        ref.set(data)

def load_json_data(filepath_json):
    # Carregar o conteúdo do outro arquivo
    with open(filepath_json, 'r', encoding='utf-8') as file:
        return json.load(file)

cred = credentials.Certificate(f"{env_dir}/credentials.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": os.getenv('DATABASE_URL')
})

def update_games_confrontation(ref, modality):
    
    games_ref = ref.child(f'modalidades/{modality}/games')
    confrontation_ref = ref.child(f'modalidades/{modality}/confrontation')

    games_json_file_path = f'{files_dir}/{modality}/games.json'
    confrontation_json_file_path = f'{files_dir}/{modality}/confrontation.json'

    set_json_data(games_json_file_path, games_ref)
    set_json_data(confrontation_json_file_path, confrontation_ref)

    logging.info(f'Games e Confrontation da modalidade {modality} atualizados com sucesso no Firebase Realtime Database.')

def update_ranking(ref, modality, groups):
    data = []
    for group in groups:
        ranking_json_file_path = f'{files_dir}/{modality}/group/ranking_{group}.json'
        data.append(get_json_data(ranking_json_file_path, group))

    ranking_ref = ref.child(f'modalidades/{modality}/ranking/')
    ranking_ref.set(data)
    logging.info(f'Ranking da modalidade {modality} atualizados com sucesso no Firebase Realtime Database.')

# Acessar o Realtime Database
ref = db.reference('/')

modality = 'FF/E'
groups = ['A', 'B', 'C']

update_games_confrontation(ref, modality)
update_ranking(ref, modality, groups)