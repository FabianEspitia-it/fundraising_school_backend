from typing import List
from fastapi import APIRouter, status, Depends, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from starlette.responses import StreamingResponse


import pandas as pd
import io
import os

from src.database import get_db
from src.users.linkedin_scraper import user_scraper

from src.users.schemas import ContactUserReq, FavFundReq, FavStartupReq, ImageUserReq, NewUserReq, RoundUserReq, UpdateUserReq, UserStartupReq
from src.users.crud import *

from src.utils.validations import check_email

user = APIRouter()


@user.get("/user/{email}", tags=["users"])
def get_user(email: str, db: Session = Depends(get_db)) -> JSONResponse:
    """
    Retrieve a user record by email.

    Args:
        email (str): The email address of the user to retrieve.
        db (Session): The database session dependency.

    Returns:
        JSONResponse: The user record if found.

    Raises:
        HTTPException: If the email is invalid (status code 400).
        HTTPException: If the user is not found (status code 404).
    """
    if not check_email(email):
        raise HTTPException(status_code=400, detail="Invalid Email")

    user_record = get_user_by_email(db, email=email)
    if not user_record:
        raise HTTPException(status_code=404, detail="Not Found")

    return user_record


@user.get("/user/education/{email}", tags=["users"])
def get_user_education(email: str, db: Session = Depends(get_db)):
    """
    Retrieves education information for a user with the specified email from the database.

    Args:
        email (str): The email address of the user whose education information is to be retrieved.
        db (Session): The database session to use for interacting with the database.

    Returns:
        UserEducation: The education information associated with the user with the specified email.

    Raises: HTTPException: If the email is invalid or if no education information is found for the user, appropriate
    HTTP status codes are raised.
    """
    if not check_email(email):
        raise HTTPException(status_code=400, detail="Invalid Email")

    user_education = get_education_by_user_email(db, email=email)
    if not user_education:
        raise HTTPException(status_code=404, detail="Not Found")

    return user_education


@user.get("/user/experience/{email}", tags=["users"])
def get_user_experience(email: str, db: Session = Depends(get_db)):
    """
    Retrieves experience information for a user with the specified email from the database.

    Args:
        email (str): The email address of the user whose experience information is to be retrieved.
        db (Session): The database session to use for interacting with the database.

    Returns:
        UserExperience: The experience information associated with the user with the specified email.

    Raises: HTTPException: If the email is invalid or if no experience information is found for the user, appropriate
    HTTP status codes are raised.
    """
    if not check_email(email):
        raise HTTPException(status_code=400, detail="Invalid Email")

    user_experience = get_experience_by_user_email(db, email=email)
    if not user_experience:
        raise HTTPException(status_code=404, detail="Not Found")

    return user_experience


@user.post("/user/contact", tags=["users"])
def update_contact_user_info(contact_user: ContactUserReq, db: Session = Depends(get_db)):
    """
    Update contact info of an user.

    Args:
        contact_user (ContactUserReq): The user contact info request containing user details.
        db (Session): The database session dependency.

    Returns:
        JSONResponse: A JSON response indicating that the user was updated.

    Raises:
        HTTPException: If the email is invalid (status code 400).
        HTTPException: If the contact email is invalid (status code 400).
    """
    if not check_email(contact_user.contact_email):
        raise HTTPException(status_code=400, detail="Invalid Contact Email")

    if not check_email(contact_user.email):
        raise HTTPException(status_code=400, detail="Invalid Email")

    amount_rows = update_contact_info_user_by_email(
        db, contact_user.email, contact_user.contact_email, contact_user.nickname)

    if amount_rows == 0:
        raise HTTPException(status_code=404, detail="Not Found")

    return JSONResponse(content={"response": "updated"}, status_code=status.HTTP_200_OK)


@user.post("/user/image", tags=["users"])
def update_contact_user_info(image_user: ImageUserReq, db: Session = Depends(get_db)):
    """
    Update image url of an user.

    Args:
        image_user (ImageUserReq): The user info request containing user details.
        db (Session): The database session dependency.

    Returns:
        JSONResponse: A JSON response indicating that the user was updated.

    Raises:
        HTTPException: If the email is invalid (status code 400).
    """
    if not check_email(image_user.email):
        raise HTTPException(status_code=400, detail="Invalid Email")

    amount_rows = update_image_url_by_email(
        db, image_user.email, image_user.image)

    if amount_rows == 0:
        raise HTTPException(status_code=404, detail="Not Found")

    return JSONResponse(content={"response": "updated"}, status_code=status.HTTP_200_OK)


@user.post("/user/round", tags=["users"])
def update_round_user_info(round_user: RoundUserReq, db: Session = Depends(get_db)):
    """
    Update round info of an user.

    Args:
        round_user (NewUserReq): The user round info request containing user details.
        db (Session): The database session dependency.

    Returns:
        JSONResponse: A JSON response indicating that the user was updated.

    Raises:
        HTTPException: If the email is invalid (status code 400).
        HTTPException: If the email is not found (status code 404).
    """
    if not check_email(round_user.email):
        raise HTTPException(status_code=400, detail="Invalid Email")

    amount_rows = update_round_info_user_by_email(
        db, round_user.email, round_user.seeking_capital, round_user.accept_terms_and_condition, round_user.round_name)

    if amount_rows == 0:
        raise HTTPException(status_code=404, detail="Not Found")

    return JSONResponse(content={"response": "updated"}, status_code=status.HTTP_200_OK)


@user.post("/user/new", tags=["users"])
def user_new(new_user: NewUserReq, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Create a new user.

    Args:
        new_user (NewUserReq): The new user request containing user details.
        background_tasks (BackgroundTasks): Background tasks manager for handling asynchronous tasks.
        db (Session): The database session dependency.

    Returns:
        JSONResponse: A JSON response indicating that the user was created.

    Raises:
        HTTPException: If the email is invalid (status code 400).
        HTTPException: If the email is already registered (status code 400).
    """
    if not check_email(new_user.email):
        raise HTTPException(status_code=400, detail="Invalid Email")

    if get_user_by_email(db=db, email=new_user.email):
        raise HTTPException(status_code=400, detail="Email registered")

    background_tasks.add_task(user_scraper, db=db, req=new_user)

    return JSONResponse(content={"response": "created"}, status_code=status.HTTP_201_CREATED)


@user.post("/user/favorite_fund", tags=["users"])
def add_favorite_fund(data: FavFundReq, db: Session = Depends(get_db)):
    """
    Add a favorite fund to a user's profile.

    Args:
        email (str): The email address of the user.
        fund_id (int): The unique identifier of the fund to add to the user's profile.
        db (Session): The database session dependency.

    Returns:
        JSONResponse: A JSON response indicating that the favorite fund was added.

    """

    fund = get_favorite_fund_by_user_id(db, data.email, data.fund_id)

    if fund:
        print("already exists", fund.fund_id, data.email)
        return JSONResponse(content={"response": "already exists"}, status_code=status.HTTP_200_OK)

    try:
        add_favorite_fund_to_user(db, data.email, data.fund_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid data request")

    return JSONResponse(content={"response": "created"}, status_code=status.HTTP_201_CREATED)


@user.get("/user/favorite_fund/csv/{email}", tags=["users"])
def get_favorite_fund_csv(email: str, db: Session = Depends(get_db)):
    """
    Retrieve a CSV file containing the favorite funds of a user.

    Args:
        email (str): The email address of the user.
        db (Session): The database session dependency.

    Returns:
        StreamingResponse: A CSV file containing the favorite funds of the user.

    Raises:
        HTTPException: If the email is invalid (status code 400).
        HTTPException: If the user is not found (status code 404).
        HTTPException: If no favorite funds are found for the user (status code 404).
    """
    if not check_email(email):
        raise HTTPException(status_code=400, detail="Invalid Email")

    user_record = get_user_by_email(db, email=email)
    if not user_record:
        raise HTTPException(status_code=404, detail="User not found")

    favorite_funds = get_favorite_funds_by_user_id(db, email=email)

    if not favorite_funds:
        raise HTTPException(
            status_code=404, detail="No favorite funds found for this user.")

    df = pd.DataFrame([fund.__dict__ for fund in favorite_funds])
    df = df.drop(columns=['_sa_instance_state'])
    df = df.drop(columns=['id'])
    df = df.drop(columns=['photo'])
    df = df.rename(columns={"crunch_base": "crunchbase",})

    
    df = df[['name', 'contact', 'description', 'location', 'website', 'linkedin', 'twitter', 'crunchbase']]
            
    # Using BytesIO to save the CSV in memory
    buffer = io.BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="text/csv", headers={"Content-Disposition": "attachment;filename=favorite_funds.csv"})


@user.delete("/user/favorite_fund/{email}/{fund_id}", tags=["users"])
def delete_favorite_fund(email: str, fund_id: int, db: Session = Depends(get_db)):
    """
    Delete a favorite fund from a user's profile.

    Args:
        email (str): The email address of the user.
        fund_id (int): The unique identifier of the fund to delete from the user's profile.
        db (Session): The database session dependency.

    Returns:
        JSONResponse: A JSON response indicating that the favorite fund was deleted.

    Raises:
        HTTPException: If the email is invalid (status code 400).
    """
    if not check_email(email):
        raise HTTPException(status_code=400, detail="Invalid Email")

    delete_favorite_fund_by_user_id(db, email, fund_id)

    return JSONResponse(content={"response": "deleted"}, status_code=status.HTTP_200_OK)


@user.post("/user/favorite_startup", tags=["users"])
def add_favorite_startup(data: FavStartupReq, db: Session = Depends(get_db)):
    """
    Add a favorite startup to a user's profile.

    Args:
        email (str): The email address of the user.
        startup_id (int): The unique identifier of the startup to add to the user's profile.
        db (Session): The database session dependency.

    Returns:
        JSONResponse: A JSON response indicating that the favorite startup was added.

    """

    add_favorite_startup_to_user(db, data.email, data.startup_id)

    return JSONResponse(content={"response": "created"}, status_code=status.HTTP_201_CREATED)


@user.get("/user/favorite_startup/csv/{email}", tags=["users"])
def get_favorite_startup_csv(email: str, db: Session = Depends(get_db)):
    """
    Retrieve a CSV file containing the favorite startups of a user.

    Args:
        email (str): The email address of the user.
        db (Session): The database session dependency.

    Returns:
        FileResponse: A CSV file containing the favorite startups of the user.

    Raises:
        HTTPException: If the email is invalid (status code 400).
        HTTPException: If the user is not found (status code 404).
        HTTPException: If no favorite startups are found for the user (status code 404).
    """
    if not check_email(email):
        raise HTTPException(status_code=400, detail="Invalid Email")

    user_record = get_user_by_email(db, email=email)
    if not user_record:
        raise HTTPException(status_code=404, detail="User not found")

    favorite_startups = get_favorite_startups_by_user_id(db, id=user_record.id)

    if not favorite_startups:
        raise HTTPException(
            status_code=404, detail="No favorite startups found for this user.")

    df = pd.DataFrame([startup for startup in favorite_startups])
    df = df.rename(columns={"phone_number": "phone number", "fund_raised": "fund raised", "one_sentence_description": "one sentence description",})

    # Using BytesIO to save the CSV in memory
    buffer = io.BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="text/csv", headers={"Content-Disposition": "attachment;filename=favorite_startups.csv"})


@user.delete("/user/favorite_startup/{email}/{startup_id}", tags=["users"])
def delete_favorite_startup(email: str, startup_id: int, db: Session = Depends(get_db)):
    """
    Delete a favorite startup from a user's profile.

    Args:
        email (str): The email address of the user.
        startup_id (int): The unique identifier of the startup to delete from the user's profile.
        db (Session): The database session dependency.

    Returns:
        JSONResponse: A JSON response indicating that the favorite startup was deleted.

    Raises:
        HTTPException: If the email is invalid (status code 400).
    """
    if not check_email(email):
        raise HTTPException(status_code=400, detail="Invalid Email")

    delete_favorite_startup_by_user_email(db, email, startup_id)

    return JSONResponse(content={"response": "deleted"}, status_code=status.HTTP_200_OK)


@user.patch("/user/update_info/{email}", tags=["users"])
def update_user_info(email: str, user_data: UpdateUserReq, db: Session = Depends(get_db)):
    """
    Update user information.

    Args:
        email (str): The email address of the user.
        user_data (dict): The user information to update.
        db (Session): The database session dependency.

    Returns:
        JSONResponse: A JSON response indicating that the user was updated.

    Raises:
        HTTPException: If the email is invalid (status code 400).
    """
    updated_user = update_user_by_email(
        db=db, email=email, user_data=user_data)

    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")

    return JSONResponse(content={"response": "updated"}, status_code=status.HTTP_200_OK)


@user.post("/user/startup", tags=["users"])
def add_user_startup(db: Session = Depends(get_db), user_data: UserStartupReq = None) -> JSONResponse:

    create_user_startup(db=db, user_data=user_data)

    return JSONResponse(content={"response": "created"}, status_code=status.HTTP_201_CREATED)


@user.post("/user/startup/bulk", tags=["users"])
def add_user_startups_bulk(background_tasks: BackgroundTasks, db: Session = Depends(get_db), user_data_list: List[UserStartupReq] = None) -> JSONResponse:
    background_tasks.add_task(create_bulk_user_startup, db=db, user_data_list=user_data_list)
    return JSONResponse(content={"response": "created"}, status_code=status.HTTP_201_CREATED)


@user.get("/user/check/{email}", tags=["users"])
def check_user(db: Session = Depends(get_db), email: str = None) -> JSONResponse:
    if not check_email(email):
        raise HTTPException(status_code=400, detail="Invalid Email")

    user_startup = get_user_startup_by_email(db, email)
    return JSONResponse(content=user_startup, status_code=status.HTTP_200_OK)


@user.get("/user/get_startup/{email}", tags=["users"])
def get_user_startup(db: Session = Depends(get_db), email: str = None) -> JSONResponse:
    if not check_email(email):
        raise HTTPException(status_code=400, detail="Invalid Email")

    user_startup = get_startup_by_user_email(db, email)
    return user_startup


@user.post("/user/classes/{class_id}", tags=["users"])
def create_class_seen_user(user_email: str, class_id: int, db: Session = Depends(get_db)):
    mark_class_seen_user(user_email, class_id, db)
    return JSONResponse(content={"response": "created"}, status_code=201)


@user.delete("/user/classes/{class_id}", tags=["users"])
def delete_class_unseen_user(user_email: str, class_id: int, db: Session = Depends(get_db)):
    mark_class_unseen_user(user_email, class_id, db)
    return JSONResponse(content={"response": "deleted"}, status_code=200)


@user.get("/user/course/{course_id}/modules", tags=["users"])
def get_users_seen_classes_in_module(user_email: str, course_id: int, db: Session = Depends(get_db)):
    return seen_classes_by_user(user_email, course_id, db)


@user.get("/user/course/{course_id}/progress", tags=["users"])
def get_course_progress(user_email: str, course_id: int, db: Session = Depends(get_db)):
    return JSONResponse(
        content={"progress": calculate_progress(user_email, course_id, db)},
        status_code=200
        )
