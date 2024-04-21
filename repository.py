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

    def get_info(self):
        return db.reference(f'info').get()
    
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
        ranking_group = db.reference(f'modalidades/{modality}/{series}/ranking/{group}').get()
        return ranking_group
    
    def get_next_games_by_local(self, dates, local):
        # Lista para armazenar todos os dados de jogos
        all_games = []

        # Recupere os dados de jogos de todas as modalidades
        
        modalities = [
            "FF/A",
            "FF/B",
            "FF/C",
            "FF/D",
            "FF/E",
            "FM/A",
            "FM/B",
            "FM/C",
            "FM/E",
            "FM/F",
            "FM/D"
        ]
        for modality in modalities:
            games_ref = db.reference(f'modalidades/{modality}/games')
            games_data = games_ref.get()

            # Verifique se existem dados de jogos para a modalidade atual
            if games_data:
                # Adicione os dados de jogos desta modalidade à lista all_games
                for game_data in games_data:
                    if (game_data['DIA'] == dates[0] or game_data['DIA'] == dates[1]) and game_data['LOCAL'] == local:
                        game_data['modalidade'] = modality
                        all_games.append(game_data)

        return all_games
