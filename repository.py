import firebase_admin
from firebase_admin import db, credentials
from dotenv import load_dotenv
import os

load_dotenv()

firebase_cred_path = os.getenv('FIREBASE_CRED_PATH')
database_url = os.getenv('DATABASE_URL')

class FirebaseRepository:
    def __init__(self):
        cred = credentials.Certificate(firebase_cred_path)
        firebase_admin.initialize_app(cred, {
            "databaseURL": database_url
        })

    def get_confrontation(self, modality, series):
        return db.reference(f'modalidades/{modality}/{series}/confrontation').get()

    def get_ranking(self, modality, series):
        return db.reference(f'modalidades/{modality}/{series}/ranking').get()

    def get_games(self, modality, series):
        games = db.reference(f'modalidades/{modality}/{series}/games').get()
        return games
    
    def get_games_by_team(self, modality, series, team=None):
        games = db.reference(f'modalidades/{modality}/{series}/games').get()
        if team:
            return [game for game in games if game.get('Mandante') == team or game.get('Visitante') == team]
        return games
    
    def get_ranking_by_group(self, modality, series, group):
        group_index = ord(group) - ord('A')
        # Referência para o nó 'ranking' no banco de dados Firebase
        ranking_group = db.reference(f'modalidades/{modality}/{series}/ranking/{group_index}/ranking').get()
        
        return ranking_group
