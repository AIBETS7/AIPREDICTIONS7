import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.database import DATABASE_URL
from models.data_models import Base, TransfermarktTeam, TransfermarktPlayer, TransfermarktTransfer
from scrapers.transfermarkt_scraper import TransfermarktScraper
from loguru import logger

SEASON = '2024'
LEAGUE_ID = 'ES1'
LEAGUE_NAME = 'LaLiga'

def main():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    # Crear tablas si no existen
    Base.metadata.create_all(engine)
    scraper = TransfermarktScraper()

    # Poblar equipos y jugadores
    logger.info('Scrapeando valores de mercado y plantillas...')
    teams_data = scraper.scrape_market_values(league_id=LEAGUE_ID, season=SEASON)
    for team in teams_data:
        team_obj = session.query(TransfermarktTeam).filter_by(name=team['team'], league=LEAGUE_NAME, season=SEASON).first()
        if not team_obj:
            team_obj = TransfermarktTeam(name=team['team'], league=LEAGUE_NAME, season=SEASON, market_value=team['team_value'])
            session.add(team_obj)
            session.flush()  # Para obtener el id
        else:
            team_obj.market_value = team['team_value']
            team_obj.last_updated = team_obj.last_updated
        for player in team['players']:
            player_obj = session.query(TransfermarktPlayer).filter_by(name=player['name'], team_id=team_obj.id).first()
            if not player_obj:
                player_obj = TransfermarktPlayer(
                    name=player['name'],
                    position=player['position'],
                    age=int(player['age']) if player['age'].isdigit() else None,
                    nationality=player['nationality'],
                    market_value=player['market_value'],
                    team_id=team_obj.id
                )
                session.add(player_obj)
            else:
                player_obj.position = player['position']
                player_obj.age = int(player['age']) if player['age'].isdigit() else None
                player_obj.nationality = player['nationality']
                player_obj.market_value = player['market_value']
                player_obj.last_updated = player_obj.last_updated
    session.commit()
    logger.info('Equipos y jugadores actualizados.')

    # Poblar traspasos
    logger.info('Scrapeando traspasos recientes...')
    transfers = scraper.scrape_transfers(league_id=LEAGUE_ID, season=SEASON, limit=50)
    for t in transfers:
        transfer_obj = session.query(TransfermarktTransfer).filter_by(
            player_name=t['player'],
            from_team=t['from_team'],
            to_team=t['to_team'],
            season=SEASON,
            league=LEAGUE_NAME
        ).first()
        if not transfer_obj:
            transfer_obj = TransfermarktTransfer(
                player_name=t['player'],
                from_team=t['from_team'],
                to_team=t['to_team'],
                fee=t['fee'],
                transfer_type=t['type'],
                season=SEASON,
                league=LEAGUE_NAME
            )
            session.add(transfer_obj)
        else:
            transfer_obj.fee = t['fee']
            transfer_obj.transfer_type = t['type']
            transfer_obj.last_updated = transfer_obj.last_updated
    session.commit()
    logger.info('Traspasos actualizados.')
    session.close()

if __name__ == '__main__':
    main() 