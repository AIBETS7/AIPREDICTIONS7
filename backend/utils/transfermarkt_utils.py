from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.database import DATABASE_URL
from models.data_models import TransfermarktTeam, TransfermarktPlayer, TransfermarktTransfer

def get_team_market_value(team_name, season='2024', league='LaLiga'):
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    team = session.query(TransfermarktTeam).filter_by(name=team_name, season=season, league=league).first()
    value = team.market_value if team else None
    session.close()
    return value

def get_team_squad(team_name, season='2024', league='LaLiga'):
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    team = session.query(TransfermarktTeam).filter_by(name=team_name, season=season, league=league).first()
    players = []
    if team:
        players = [
            {
                'name': p.name,
                'position': p.position,
                'age': p.age,
                'nationality': p.nationality,
                'market_value': p.market_value
            } for p in team.players
        ]
    session.close()
    return players

def get_recent_transfers(team_name=None, player_name=None, season='2024', league='LaLiga', limit=10):
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    q = session.query(TransfermarktTransfer).filter_by(season=season, league=league)
    if team_name:
        q = q.filter((TransfermarktTransfer.from_team == team_name) | (TransfermarktTransfer.to_team == team_name))
    if player_name:
        q = q.filter_by(player_name=player_name)
    transfers = q.order_by(TransfermarktTransfer.last_updated.desc()).limit(limit).all()
    result = [
        {
            'player_name': t.player_name,
            'from_team': t.from_team,
            'to_team': t.to_team,
            'fee': t.fee,
            'transfer_type': t.transfer_type,
            'season': t.season,
            'league': t.league,
            'last_updated': t.last_updated.isoformat() if t.last_updated else None
        } for t in transfers
    ]
    session.close()
    return result 