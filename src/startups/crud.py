from sqlalchemy.orm import Session, joinedload

from src.models import *

from src.users.crud import get_user_by_email, get_favorite_startups_by_user_id


def get_all_startups(db: Session, page: int, limit: int, user_email: str, location: str = None, sector: str = None) -> list[dict]:

    # Get the user from the database
    user = get_user_by_email(db, user_email)

    if not user:
        raise ValueError("User not found")

    # Retrieve favorite startups
    favorite_startups = get_favorite_startups_by_user_id(db, user_email)
    favorite_startups_ids = {startup.id for startup in favorite_startups}

    # Create the initial query with joinedload options
    query = db.query(Startup).options(
        joinedload(Startup.sector)
    )

    if sector:
        print("Sector filter applied", sector)
        query = query.join(Startup.sector).filter(Sector.name == sector)

    # Apply pagination after filters and sorting
    query = query.offset((page - 1) * limit).limit(limit)

    # Retrieve funds and convert to list of dicts with 'favorite' field
    startups = query.all()

    startups_with_favorite = []
    for startup in startups:
        startup_dict = startup.__dict__.copy()
        startup_dict['favorite'] = startup.id in favorite_startups_ids
        startups_with_favorite.append(startup_dict)

    return startups_with_favorite


def get_startup_by_id(db: Session, startup_id: int) -> Startup:
    return db.query(Startup).filter(Startup.id == startup_id).first()
