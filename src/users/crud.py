from sqlalchemy.orm import Session

from src.users.schemas import NewUserReq

import src.models as models


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
    user_first_name = new_user.name.split()[0]
    user = models.User(
        first_name=user_first_name,
        email=new_user.email,
        photo_url=new_user.linkedin_picture
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
        raise Exception("User not found")


def get_favorite_fund_by_user_id(db: Session, email: str, fund_id: int) -> models.UserFundFavorite:
    user = get_user_by_email(db, email)
    if user:
        return db.query(models.UserFundFavorite).filter(models.UserFundFavorite.user_id == user.id, models.UserFundFavorite.fund_id == fund_id).first()
    else:
        raise Exception("User not found")


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
        raise Exception("User not found")


def add_favorite_startup_to_user(db: Session, email: str, startup_id: int) -> None:
    user = get_user_by_email(db, email)
    if user:
        user_startup = models.UserStartupFavorite(
            user_id=user.id, startup_id=startup_id)
        db.add(user_startup)
        db.commit()
        db.refresh(user_startup)
    else:
        raise Exception("User not found")


def get_favorite_startups_by_user_id(db: Session, email: str) -> list[models.Startup]:

    query = db.query(models.Startup).join(models.UserStartupFavorite).join(
        models.User).filter(models.User.email == email).all()

    return query


def delete_favorite_startup_by_user_id(db: Session, email: str, startup_id: int) -> None:
    user = get_user_by_email(db, email)
    if user:
        db.query(models.UserStartupFavorite).filter(models.UserStartupFavorite.user_id ==
                                                    user.id, models.UserStartupFavorite.startup_id == startup_id).delete()
        db.commit()
    else:
        raise Exception("User not found")
