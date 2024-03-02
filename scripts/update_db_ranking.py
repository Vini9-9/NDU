import firebase_admin
from firebase_admin import credentials, db
import json
from dotenv import load_dotenv
import os

load_dotenv()

def get_json_data(json_file_path, group):
    with open(json_file_path, 'r') as file:
        data = {
            "group": group,
            "ranking": json.load(file)
        }
        return data
        

def load_json_data(filepath_json):
    # Carregar o conteúdo do outro arquivo
    with open(filepath_json, 'r') as file:
        return json.load(file)

cred = credentials.Certificate("../env/credentials.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": os.getenv('DATABASE_URL')
})

# Acessar o Realtime Database
ref = db.reference()

data_son = load_json_data('../files/modalities.json')
values_json = [item['value'] for item in data_son]
groups = ['A', 'B']

for modality in values_json:
    data = []
    for group in groups:
        ranking_ref = ref.child('modalidades/' + modality + '/ranking/')
        ranking_json_file_path = '../files/' + modality + '/group/ranking_' + group + '.json'
        data.append(get_json_data(ranking_json_file_path, group))
    ranking_ref.set(data)
    print('Ranking da modalidade ' + modality + ' atualizados com sucesso no Firebase Realtime Database.')