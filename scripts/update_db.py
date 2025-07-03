import firebase_admin
from firebase_admin import credentials, db
import json
from dotenv import load_dotenv
import os
import datetime
import logging

INFO_DB_FILE = os.path.join(os.getcwd(), "info_db.json")

data_hora_atual = datetime.datetime.now()

dia_atual = data_hora_atual.strftime("%d/%m/%Y")
# Configuração básica de logging
logging.basicConfig(filename='../logs/log_db_' + data_hora_atual.strftime("%Y-%m-%d_%H-%M-%S") + '.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

def set_json_data(json_file_path, ref):
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        ref.set(data)

def load_json_data(filepath_json):
    # Carregar o conteúdo do outro arquivo
    with open(filepath_json, 'r', encoding='utf-8') as file:
        return json.load(file)

def update_info_data(ref):
    with open(INFO_DB_FILE, "r") as file:
        data = json.load(file)
        data["dbUpdateDate"] = dia_atual
        boletim_date = data["boletimDate"]  

    ref.child('info/dbUpdatedDate').set(dia_atual)
    logging.info(f'info/dbUpdatedDate atualizado com valor {dia_atual}.')
    ref.child('info/boletimDate').set(boletim_date)
    logging.info(f'info/boletimDate atualizado com valor {boletim_date}.')

cred = credentials.Certificate("../env/credentials.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": os.getenv('DATABASE_URL')
})

# Acessar o Realtime Database
ref = db.reference()

data_son = load_json_data('../files/modalities.json')
values_json = [item['value'] for item in data_son]

for modality in values_json:
    games_ref = ref.child('modalidades/' + modality + '/games')
    confrontation_ref = ref.child('modalidades/' + modality + '/confrontation')

    games_json_file_path = '../files/' + modality + '/games.json'
    confrontation_json_file_path = '../files/' + modality + '/confrontation.json'

    set_json_data(games_json_file_path, games_ref)
    set_json_data(confrontation_json_file_path, confrontation_ref)

    logging.info(f'Games e Confrontation da modalidade {modality} atualizados com sucesso no Firebase Realtime Database.')

update_info_data(ref)