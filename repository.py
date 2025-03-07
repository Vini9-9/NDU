import firebase_admin
from firebase_admin import db, credentials
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

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
        return db.reference('info').get()
    
    def get_flags(self):
        return db.reference('flags').get()
    
    def get_confrontation(self, modality, series):
        return db.reference(f'modalidades/{modality}/{series}/confrontation').get()

    def get_ranking(self, modality, series):
        return db.reference(f'modalidades/{modality}/{series}/ranking').get()

    def get_games(self, modality, series):
        games = db.reference(f'modalidades/{modality}/{series}/games').get()
        return games
    
    def get_playoff_games(self, modality, series):
        playoff = db.reference(f'modalidades/{modality}/{series}/playoff').get()
        return playoff
    
    def get_games_by_team(self, modality, series, team=None):
        games = db.reference(f'modalidades/{modality}/{series}/games').get()
        if team:
            return [game for game in games if game.get('Mandante') == team or game.get('Visitante') == team]
        return games
    
    def get_ranking_by_group(self, modality, series, group):
        ranking_group = db.reference(f'modalidades/{modality}/{series}/ranking/{group}').get()
        return ranking_group
    
    def get_next_games_by_local(self, local):
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
                    if (self.check_date_between_week(game_data.get('DIA'))) and game_data.get('LOCAL') == local:
                        game_data['modalidade'] = modality
                        all_games.append(game_data)

        return all_games

    def is_date_between(self, date_str, initial_date_str, final_date_str):
        if date_str:
            date = datetime.strptime(date_str, '%Y-%m-%d')
            initial_date = datetime.strptime(initial_date_str, '%Y-%m-%d')
            final_date = datetime.strptime(final_date_str, '%Y-%m-%d')
            return initial_date <= date <= final_date
        return False

    def check_date_between_week(self, date_str):
        current_date = datetime.now()
        initial_date = current_date - timedelta(days=1)
        final_date = current_date + timedelta(days=6 - current_date.weekday())

        if current_date.weekday() == 6:
            final_date = current_date

        return self.is_date_between(date_str, initial_date.strftime('%Y-%m-%d'), final_date.strftime('%Y-%m-%d'))