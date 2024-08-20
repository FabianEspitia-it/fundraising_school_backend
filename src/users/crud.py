from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload


import pandas as pd

from src.users.schemas import *

from src.course.crud import get_modules_by_course_id

import src.models as models
from src.utils.truora_method import send_outbound_message


def get_user_by_email(db: Session, email: str) -> models.User:
    return db.query(models.User).filter(models.User.email == email).first()


def update_contact_info_user_by_email(db: Session, email: str, contact_email: str, nickname: str) -> int:
    amount_rows: int = db.query(models.User).filter(models.User.email == email).update(
        {models.User.contact_email: contact_email, models.User.nickname: nickname})
    db.commit()

    return amount_rows


def update_image_url_by_email(db: Session, email: str, image: str) -> int:
    amount_rows: int = db.query(models.User).filter(
        models.User.email == email).update({models.User.photo_url: image})
    db.commit()

    return amount_rows


def update_round_info_user_by_email(db: Session, email: str, seeking_capital: bool, accept_terms_and_condition: bool, round_stage: str | None) -> int:
    if seeking_capital:
        round_db: models.Round = db.query(models.Round).filter(
            models.Round.stage == round_stage).first()
        amount_rows: int = db.query(models.User).filter(models.User.email == email).update(
            {models.User.seeking_capital: seeking_capital, models.User.round_id: round_db.id, models.User.terms_conditions: accept_terms_and_condition})

    else:
        amount_rows: int = db.query(models.User).filter(models.User.email == email).update(
            {models.User.seeking_capital: seeking_capital, models.User.round_id: None, models.User.terms_conditions: accept_terms_and_condition})

    db.commit()
    return amount_rows


def create_user_principal_data(db: Session, new_user: NewUserReq) -> int:
    print(new_user)
    user_first_name = new_user.name.split()[0]
    user = models.User(
        first_name=user_first_name,
        email=new_user.email,
        photo_url=new_user.linkedin_picture,
        courses=db.query(models.Course).all()
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user.id


def get_education_by_user_email(db: Session, email: str) -> list[models.Education]:
    return db.query(models.Education).join(models.User).filter(models.User.email == email).all()


def get_experience_by_user_email(db: Session, email: str) -> list[models.Education]:
    return db.query(models.Experience).join(models.User).filter(models.User.email == email).all()


def create_bulk_education(db: Session, education: list[models.Education]) -> None:
    db.add_all(education)
    db.commit()


def create_bulk_experience(db: Session, experiences: list[models.Experience]) -> None:
    db.add_all(experiences)
    db.commit()


def add_favorite_fund_to_user(db: Session, email: str, fund_id: int) -> None:
    user = get_user_by_email(db, email)
    if user:
        user_fund = models.UserFundFavorite(user_id=user.id, fund_id=fund_id)
        db.add(user_fund)
        db.commit()
        db.refresh(user_fund)
    else:
        raise HTTPException(status_code=404, detail="User not found")


def get_favorite_fund_by_user_id(db: Session, email: str, fund_id: int) -> models.UserFundFavorite:
    user = get_user_by_email(db, email)
    if user:
        return db.query(models.UserFundFavorite).filter(models.UserFundFavorite.user_id == user.id, models.UserFundFavorite.fund_id == fund_id).first()
    else:
        raise HTTPException(status_code=404, detail="User not found")


def get_favorite_funds_by_user_id(db: Session, email: str) -> list[models.Fund]:

    query = db.query(models.Fund).join(models.UserFundFavorite).join(
        models.User).filter(models.User.email == email).all()

    return query


def delete_favorite_fund_by_user_id(db: Session, email: str, fund_id: int) -> None:
    user = get_user_by_email(db, email)
    if user:
        db.query(models.UserFundFavorite).filter(models.UserFundFavorite.user_id ==
                                                 user.id, models.UserFundFavorite.fund_id == fund_id).delete()
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="User not found")


def add_favorite_startup_to_user(db: Session, email: str, startup_id: int) -> None:
    user = get_user_by_email(db, email)
    if user:
        user_startup = models.UserStartupFavorite(
            user_id=user.id, startup_id=startup_id)
        db.add(user_startup)
        db.commit()
        db.refresh(user_startup)
    else:
        raise HTTPException(status_code=404, detail="User not found")


def get_favorite_startups_by_user_id(db: Session, id: int):
    query = db.query(models.Startup).join(models.UserStartupFavorite).join(
        models.User).filter(models.User.id == id).all()

    return query


def map_ids_to_names(db: Session, df: pd.DataFrame, column_name: str, model, attr_name: str):

    df_filtered = df[df[column_name].notna()]

    ids = df_filtered[column_name].tolist()

    records = db.query(model).filter(model.id.in_(ids)).all()

    record_dict = {record.id: getattr(record, attr_name) for record in records}

    new_column_name = column_name.replace('_id', '')
    df[new_column_name] = df[column_name].map(record_dict)

    df[new_column_name] = df[new_column_name].fillna('')

    df = df.drop(columns=[column_name])

    return df


def delete_favorite_startup_by_user_email(db: Session, email: str, startup_id: int) -> None:
    user = get_user_by_email(db, email)
    if user:
        db.query(models.UserStartupFavorite).filter(models.UserStartupFavorite.user_id ==
                                                    user.id, models.UserStartupFavorite.startup_id == startup_id).delete()
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="User not found")


def update_user_by_email(db: Session, email: str, user_data: UpdateUserReq) -> models.User:

    user = db.query(models.User).filter(
        models.User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)

    return user


def create_user_startup(db: Session, user_data: UserStartupReq) -> None:
    user = models.User(
        nickname=user_data.nickname,
        email=user_data.email,
        linkedin_url=user_data.linkedin_url,
        phone_number=user_data.phone_number,
        location=user_data.location,
        courses=db.query(models.Course).all()
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    startup = db.query(models.Startup).filter(
        models.Startup.name == user_data.startup_name.title()).first()

    if startup:
        user_startup = models.StartupUser(
            user_id=user.id,
            startup_id=startup.id
        )
        db.add(user_startup)
        db.commit()

    else:
        raise HTTPException(status_code=404, detail="Startup not found")


def create_user_startup_new(db: Session, user_data: UserStartup) -> None:

    user = db.query(models.User).filter(
        user_data.email == models.User.email).first()

    update_data = user_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)

    startup = db.query(models.Startup).filter(
        models.Startup.name == user_data.startup_name.title()).first()

    if startup:
        user_startup = models.StartupUser(
            user_id=user.id,
            startup_id=startup.id
        )
        db.add(user_startup)
        db.commit()
    else:
        startup = models.Startup(
            name=user_data.startup_name.title(),
        )
    db.add(startup)
    db.commit()
    db.refresh(startup)

    relationship = db.query(models.StartupUser).filter(
        models.StartupUser.user_id == user.id).first()

    if not relationship:
        user_startup = models.StartupUser(
            user_id=user.id,
            startup_id=startup.id
        )
        db.add(user_startup)
        db.commit()

    #send_outbound_message(phone_number=user.phone_number, country_code=user.country_code)

    return user


def get_user_fund_by_email(db: Session, email: str) -> bool:

    user = db.query(models.User).filter(models.User.email == email).first()

    if user:
        connection = db.query(models.FundUsers).filter(
            models.FundUsers.user_id == user.id).first()
        if connection or user.investment_geography is not None:
            return {"response": "fund"}
        else:
            return {"response": "guest"}
    else:
        raise HTTPException(status_code=404, detail="User not found")


def get_user_startup_by_email(db: Session, email: str) -> bool:

    user = db.query(models.User).filter(models.User.email == email).first()

    if user:
        connection = db.query(models.StartupUser).filter(
            models.StartupUser.user_id == user.id).first()
        if connection:
            return {"response": "startup"}
        else:
            return get_user_fund_by_email(db, email)
    else:
        raise HTTPException(status_code=404, detail="User not found")


def get_startup_by_user_email(db: Session, email: str) -> models.Startup:
    user = db.query(models.User).filter(models.User.email == email).first()
    if user:
        startup = db.query(models.Startup).join(models.StartupUser).filter(
            models.StartupUser.user_id == user.id).options(
            joinedload(models.Startup.country),
            joinedload(models.Startup.traction),
            joinedload(models.Startup.sector),
            joinedload(models.Startup.round)
        ).first()
        return startup
    else:
        raise HTTPException(status_code=404, detail="User not found")


def mark_class_unseen_user(user_email: str, class_id: int, db: Session):
    user: models.User = db.query(models.User).filter(
        models.User.email == user_email).first()
    user_class: models.UserClass = db.query(models.UserClass).filter(
        models.UserClass.class_id == class_id and models.UserClass.user_id == user.id).first()
    db.delete(user_class)
    db.commit()
    return user_class


def seen_classes_by_user(user_email: str, db: Session):
    user: models.User = db.query(models.User).filter(
        models.User.email == user_email).first()
    if not user:
        return []

    classes = db.query(models.Class).join(models.UserClass
                                          ).filter(
        models.UserClass.user_id == user.id,
    ).filter(
        models.UserClass.class_id == models.Class.id,
    ).all()
    return classes


def calculate_progress(user_email: str, course_id: int, db: Session):
    seen_classes: list[models.Class] = seen_classes_by_user(user_email, db)
    modules: list[models.Module] = get_modules_by_course_id(db, course_id)
    total_classes: list[models.Class] = []

    for module in modules:
        total_classes = total_classes + module.classes

    seen_classes_into_course: list[models.Class] = list(
        filter(lambda c: c in total_classes, seen_classes))

    percentage_progress: int = 0
    if int(len(total_classes)) != 0:
        percentage_progress: int = int(
            len(seen_classes_into_course)) / int(len(total_classes))

    return f"{int(percentage_progress * 100)}%"

"""
def get_all_users(db: Session):
    return db.query(models.User).all()
"""

def create_normal_user(db: Session, user_data: UserNormal):
    # from src.users.linkedin_scraper import search_linkedin_url
    user = models.User(
        nickname=user_data.nickname,
        email=user_data.email,
        country_code=user_data.country_code,
        linkedin_url=None,
        phone_number=user_data.phone_number,
        location=user_data.location,
        courses=db.query(models.Course).all()
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def add_linkedin_information(user_email: str, db: Session):
    user = db.query(models.User).filter(
        models.User.email == user_email).first()

    from src.users.linkedin_scraper import linkedin_public_identifier, scraper_linkedin_profile
    user_public_identifier = linkedin_public_identifier(user.linkedin_url)
    scraper_linkedin_profile(db, user_public_identifier, user.id)


def create_attendee_user(db: Session, user_data: UserAttendee):

    user = db.query(models.User).filter(
        user_data.email == models.User.email).first()

    update_data = user_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)

    startup = db.query(models.Startup).filter(
        models.Startup.name == user_data.startup_name).first()

    if startup:
        user_startup = models.StartupUser(
            user_id=user.id,
            startup_id=startup.id
        )
        db.add(user_startup)
        db.commit()
    else:
        new_startup = models.Startup(
            name=user_data.startup_name,
        )
        db.add(new_startup)
        db.commit()
        db.refresh(new_startup)

        user_startup = models.StartupUser(
            user_id=user.id,
            startup_id=new_startup.id
        )
        db.add(user_startup)
        db.commit()

    return user


def create_investor_user(db: Session, user_data: UserInvestor):

    stage = db.query(models.Round).filter(
        models.Round.stage == user_data.investment_stage).first()

    if not stage:
        stage = models.Round(
            stage=user_data.investment_stage
        )
        db.add(stage)
        db.commit()
        db.refresh(stage)

    user = db.query(models.User).filter(
        user_data.email == models.User.email).first()

    update_data = user_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    user.round_id = stage.id

    db.commit()
    db.refresh(user)

    return user


def create_users_fund_ctw(db: Session, users_data: list[UserFundCtw]) -> None:

    for user_data in users_data:
        user = models.User(
            nickname=user_data.nickname,
            email=user_data.email,
            linkedin_url=user_data.linkedin_url,
            role=user_data.role,
            photo_url=user_data.photo,
            courses=db.query(models.Course).all()
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        fund = db.query(models.Fund).filter(
            models.Fund.name == user_data.fund_name.title()).first()

        if fund:
            user_fund = models.FundUsers(
                user_id=user.id,
                fund_id=fund.id
            )
            db.add(user_fund)
            db.commit()

        else:
            raise HTTPException(status_code=404, detail="User not found")


def update_user_photo_and_linkedin(db: Session, user_data: UpdateLinkedinAndPhotoUrl):
    user_to_update = db.query(models.User).filter(
        models.User.email == user_data.email).first()

    if not user_to_update:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user_to_update, key, value)

    db.commit()
    db.refresh(user_to_update)


def get_all_users(db: Session) -> list[dict]:
    users = db.query(
        models.User.nickname,
        models.User.email,
        models.User.country_code,
        models.User.phone_number
    ).all()

    final_users: list[dict] = []

    for user in users:
        user_dict = {
            'full_name': user.nickname,
            'email': user.email,
            'country_code': user.country_code,
            'phone_number': user.phone_number,
            'kind': get_user_startup_by_email(db, user.email)
        }
        final_users.append(user_dict)

    return final_users


def delete_startup_user_conn(user_email: str, db: Session):
    user = db.query(models.User).filter(
        models.User.email == user_email).first()
    startup_user = db.query(models.StartupUser).filter(
        models.StartupUser.user_id == user.id).first()
    db.delete(startup_user)
    db.commit()
    return startup_user

