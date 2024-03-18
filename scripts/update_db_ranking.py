import firebase_admin
from firebase_admin import credentials, db
import json
from dotenv import load_dotenv
import os
import datetime
import logging

data_hora_atual = datetime.datetime.now()

# Configuração básica de logging
logging.basicConfig(filename='../logs/log_db_ranking_' + data_hora_atual.strftime("%Y-%m-%d_%H-%M-%S") + '.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

def get_json_data(json_file_path, group):
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = {
            "group": group,
            "ranking": json.load(file)
        }
        return data
        

def load_json_data(filepath_json):
    # Carregar o conteúdo do outro arquivo
    with open(filepath_json, 'r', encoding='utf-8') as file:
        return json.load(file)

cred = credentials.Certificate("../env/credentials.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": os.getenv('DATABASE_URL')
})

# Acesse o Realtime Database com o token personalizado
ref = db.reference('/')

data_json = load_json_data('../files/modalities.json')
values_json = [item['value'] for item in data_json]
groups = ['A', 'B']

for modality in values_json:
    data = []
    for group in groups:
        ranking_ref = ref.child(f'modalidades/{modality}/ranking/')
        ranking_json_file_path = f'../files/{modality}/group/ranking_{group}.json'
        data.append(get_json_data(ranking_json_file_path, group))
    ranking_ref.set(data)
    logging.info(f'Ranking da modalidade ' + modality + ' atualizados com sucesso no Firebase Realtime Database.')