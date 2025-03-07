import firebase_admin
from firebase_admin import credentials, db
import json
from dotenv import load_dotenv
import os
import datetime
import logging

data_hora_atual = datetime.datetime.now()

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

cred = credentials.Certificate("../env/credentials.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": os.getenv('DATABASE_URL')
})

# Acessar o Realtime Database
ref = db.reference()

data_son = load_json_data('../files/modalities.json')
values_json = [item['value'] for item in data_son]

for modality in values_json:
    playoff_ref = ref.child('modalidades/' + modality + '/playoff')

    playoff_json_file_path = '../files/' + modality + '/playoff.json'

    set_json_data(playoff_json_file_path, playoff_ref)

    logging.info('playoff da modalidade ' + modality + ' atualizados com sucesso no Firebase Realtime Database.')
