import os
from uuid import uuid4

from fastapi import UploadFile, HTTPException

from google.cloud import storage
from google.oauth2 import service_account

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from src.models import *

from src.startups.schemas import NewStartupReq, UpdateStartupReq, CreateBulkStartupReq
from src.users.crud import get_user_by_email, get_favorite_startups_by_user_id

from sqlalchemy.exc import SQLAlchemyError

from sqlalchemy.orm import Session, joinedload

import src.models as models


AWS_BUCKET = os.getenv("AWS_BUCKET")
SUPPORTED_IMAGES_TYPES = {
    'image/jpeg': 'jpg',
    'image/png': 'png',
    'image/svg': 'svg'
}


def get_all_startups(db: Session, page: int, limit: int, user_email: str, sector: str = None, country: str = None, traction: str = None, term: str = None):
    # Get the user from the database
    user = get_user_by_email(db, user_email)

    if not user:
        raise ValueError("User not found")

    # Retrieve favorite startups
    favorite_startups = get_favorite_startups_by_user_id(db, user.id)
    favorite_startups_ids = {startup.id for startup in favorite_startups}

    # Create the initial query with joinedload options
    if term:
        query = db.query(Startup).filter(func.lower(Startup.name).like(f"%{term.lower()}%")).options(
            joinedload(Startup.sector),
            joinedload(Startup.traction),
            joinedload(Startup.country)
        )
    else:
        query = db.query(Startup).options(
            joinedload(Startup.sector),
            joinedload(Startup.traction),
            joinedload(Startup.country)
        )

    query = query.filter(
        Startup.name.isnot(None),
        Startup.description.isnot(None),
        Startup.photo.isnot(None),
        Startup.email.isnot(None),
        Startup.one_sentence_description.isnot(None),
        Startup.deck.isnot(None),
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


def total_startups(db: Session, sector: str = None, country: str = None, traction: str = None, term: str = None) -> int:
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

    query = query.filter(
        Startup.name.isnot(None),
        Startup.description.isnot(None),
        Startup.photo.isnot(None),
        Startup.email.isnot(None),
        Startup.one_sentence_description.isnot(None),
        Startup.deck.isnot(None),
    )

    if term:
        query = query.filter(func.lower(
            Startup.name).like(f"%{term.lower()}%"))

    if country:
        query = query.filter(Startup.country.has(name=country))

    if sector:
        query = query.filter(Startup.sector.has(name=sector))

    if traction:
        query = query.filter(Startup.traction.has(name=traction))

    return query.count()


def get_startup_by_id(db: Session, startup_id: int) -> Startup:
    return db.query(Startup).filter(Startup.id == startup_id).options(
        joinedload(Startup.country)
    ).first()


def create_startup(db: Session, startup: NewStartupReq) -> Startup:
    startup_data = startup.model_dump()
    new_startup = Startup(
        name=startup_data["name"],
        email=startup_data["email"],
        description=startup_data["description"],
        phone_number=startup_data["phone_number"],
        country=startup_data["country"],
        website=startup_data["website"],
        linkedin=startup_data["linkedin"],
        photo=startup_data["photo"],
        calendly=startup_data["calendly"],
        sector_id=db.query(Sector).filter(
            Sector.name == startup_data["sector"]).first().id,
        round_id=db.query(Round).filter(
            Round.stage == startup_data["round"]).first().id,
        traction_id=db.query(Traction).filter(
            Traction.name == startup_data["traction"]).first().id
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
        if key == 'country':
            country = db.query(Country).filter(Country.name == value).first()
            if not country:
                db.add(Country(name=value))
                db.commit()

                country = db.query(Country).filter(
                    Country.name == value).first()

            startup_to_update.country_id = country.id
        elif key == 'sector':
            sector = db.query(Sector).filter(Sector.name == value).first()
            if not sector:
                db.add(Sector(name=value))
                db.commit()

                sector = db.query(Sector).filter(Sector.name == value).first()
            startup_to_update.sector = sector
        elif key == 'traction':
            traction = db.query(Traction).filter(
                Traction.name == value).first()
            if not traction:

                db.add(Traction(name=value))
                db.commit()

                traction = db.query(Traction).filter(
                    Traction.name == value).first()
            startup_to_update.traction = traction
            

        elif key == 'round':
            round = db.query(Round).filter(Round.stage == value).first()
            if not round:
                db.add(Round(stage=value))
                db.commit()

                round = db.query(Round).filter(Round.stage == value).first()
            startup_to_update.round = round
        else:
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


def get_users_by_startup_name(db: Session, startup_name: str):
    startup = db.query(Startup).filter(Startup.name == startup_name).first()

    if not startup:
        raise ValueError("Startup not found")

    users_in_startup = db.query(User).join(StartupUser).filter(
        StartupUser.startup_id == startup.id).all()

    return users_in_startup


async def gcs_upload(startup_photo_file: UploadFile, startup_id: int, file_type: str) -> str:

    bucket_name = os.getenv('GCS_BUCKET_NAME')
    if not bucket_name:
        raise HTTPException(
            status_code=500, detail="GCS_BUCKET_NAME environment variable is not set")


    if os.getenv('ENVIROMENT') == 'production':
        credentials = None
        client = storage.Client()
    else:
        credentials = service_account.Credentials.from_service_account_file(
            os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        )
        client = storage.Client(credentials=credentials)

    bucket = client.bucket(bucket_name)
    blob = bucket.blob(
        f'startups/{uuid4()}.{SUPPORTED_IMAGES_TYPES[file_type]}')

    startup_photo_file.file.seek(0)
    blob.upload_from_file(startup_photo_file.file)
    # blob.make_public()

    return blob.public_url


def update_startup_photo(db: Session, startup_photo_link: str, startup_id: str) -> str:
    db.query(models.Startup).filter(models.Startup.id ==
                                    startup_id).update({'photo': startup_photo_link})
    db.commit()
