from sqlalchemy.orm import Session, joinedload

from src.models import *

from src.startups.schemas import NewStartupReq, UpdateStartupReq, CreateBulkStartupReq
from src.users.crud import get_user_by_email, get_favorite_startups_by_user_id

from sqlalchemy.exc import SQLAlchemyError


def get_all_startups(db: Session, page: int, limit: int, user_email: str, sector: str = None, country: str = None, traction: str = None):
    # Get the user from the database
    user = get_user_by_email(db, user_email)

    if not user:
        raise ValueError("User not found")

    # Retrieve favorite startups
    favorite_startups = get_favorite_startups_by_user_id(db, user.id)
    favorite_startups_ids = {startup.id for startup in favorite_startups}

    # Create the initial query with joinedload options
    query = db.query(Startup).options(
        joinedload(Startup.sector),
        joinedload(Startup.traction),
        joinedload(Startup.country)
    )

    if sector:
        print("Sector filter applied", sector)
        query = query.filter(Startup.sector.has(name=sector))

    if country:
        print("Location filter applied", country)
        query = query.filter(Startup.country.has(name=country))

    if traction:
        print("Round filter applied", traction)
        query = query.filter(Startup.traction.has(name=traction))

    # Apply pagination after filters and sorting
    query = query.offset((page - 1) * limit).limit(limit)

    # Retrieve startups and convert to list of dicts with 'favorite' field
    startups = query.all()

    startups_with_favorite = []
    for startup in startups:
        startup_dict = startup.__dict__.copy()
        startup_dict['favorite'] = startup.id in favorite_startups_ids
        startups_with_favorite.append(startup_dict)

    return startups_with_favorite


def total_startups(db: Session, sector: str = None, country: str = None, traction: str = None) -> int:
    """
    Retrieves the total number of startups in the database.

    Args:
        db (Session): Database session object.
        sector (str, optional): Sector filter.
        country (str, optional): Country filter.
        traction (str, optional): Traction filter.

    Returns:
        int: Total number of startups.
    """
    
    query = db.query(Startup)
    
    if country:
        query = query.filter(Startup.country.has(name=country))

    if sector:
        query = query.filter(Startup.sector.has(name=sector))

    if traction:
        query = query.filter(Startup.traction.has(name=traction))

    

    return query.count()


def get_startup_by_id(db: Session, startup_id: int) -> Startup:
    return db.query(Startup).filter(Startup.id == startup_id).first()


def create_startup(db: Session, startup: NewStartupReq) -> Startup:
    startup_data = startup.model_dump()
    new_startup = Startup(
        name=startup_data["name"],
        email=startup_data["email"],
        description=startup_data["description"],
        country_code=startup_data["country_code"],
        whatsapp=startup_data["whatsapp"],
        location=startup_data["location"],
        website=startup_data["website"],
        linkedin=startup_data["linkedin"],
        photo=startup_data["photo"],
        calendly=startup_data["calendly"],
        sector_id=db.query(Sector).filter(
            Sector.name == startup_data["sector"]).first().id,
        round_id=db.query(Round).filter(
            Round.stage == startup_data["round"]).first().id,
        checksize_id=db.query(CheckSize).filter(
            CheckSize.size == startup_data["checksize"]).first().id
    )
    db.add(new_startup)
    db.commit()
    db.refresh(new_startup)
    return new_startup


def update_startup_by_id(db: Session, startup_id: int, startup: UpdateStartupReq) -> Startup:

    startup_to_update = db.query(Startup).filter(
        Startup.id == startup_id).first()

    if not startup_to_update:
        raise ValueError("Startup not found")

    update_data = startup.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(startup_to_update, key, value)

    db.commit()
    db.refresh(startup_to_update)

    return startup_to_update


def get_or_create(db: Session, model, **kwargs):
    instance = db.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        db.add(instance)
        db.commit()
        db.refresh(instance)
        return instance


def create_bulk_startup(db: Session, startup_data_list: list[CreateBulkStartupReq]):
    try:
        for startup_data in startup_data_list:

            sector = get_or_create(db, Sector, name=startup_data.sector)

            country = get_or_create(db, Country, name=startup_data.country)

            traction = get_or_create(db, Traction, name=startup_data.traction)

            startup = Startup(
                name=startup_data.name,
                description=startup_data.description,
                phone_number=startup_data.phone_number,
                country=country,
                website=startup_data.website,
                photo=startup_data.photo,
                sector=sector,
                traction=traction,
                fund_raised=startup_data.fund_raised
            )

            db.add(startup)

        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise e
    

def get_countries(db: Session):
    return db.query(Country).all()


def get_sectors(db: Session):
    return db.query(Sector).all()


def get_tractions(db: Session):
    return db.query(Traction).all()


def get_country_startups(db: Session):
    return db.query(Startup.country_id).all()


def get_sector_startups(db: Session):
    return db.query(Startup.sector_id).all()


def get_traction_startups(db: Session):
    return db.query(Startup.traction_id).all()


