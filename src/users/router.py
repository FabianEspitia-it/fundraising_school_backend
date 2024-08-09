from typing import List
from fastapi import APIRouter, status, Depends, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from starlette.responses import StreamingResponse
from openpyxl import Workbook
from openpyxl.styles import Font, Border, Side


import pandas as pd
import io
import os


from src.database import get_db
from src.users.linkedin_scraper import user_scraper

from src.users.schemas import *
from src.users.crud import *

from src.models import Country, Round, Sector, Traction

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
            
    
    
    empty_row = pd.DataFrame([[''] * len(df.columns)], columns=df.columns)

    startups_title = pd.DataFrame([['Your_Favorite_Funds'] + [''] * (len(df.columns) - 1)], columns=df.columns)

 
    df = pd.concat([empty_row, startups_title, pd.DataFrame([df.columns], columns=df.columns), df], ignore_index=True)

    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, header=False)
        worksheet = writer.sheets['Sheet1']

        for cell in worksheet["A3:H3"]:
            for c in cell:
                c.font = Font(bold=True)

        thin_border = Border(left=Side(style='thin'), 
                             right=Side(style='thin'), 
                             top=Side(style='thin'), 
                             bottom=Side(style='thin'))
        
        worksheet['A2'].font = Font(bold=True)

        #Your Favorite Funds Border
        worksheet['A2'].border = thin_border
        
        end_row = 3 + len(favorite_funds)
        
        #funds informarion border
        for row in worksheet.iter_rows(min_row=3, max_row=end_row, min_col=1, max_col=worksheet.max_column):
            for cell in row:
                cell.border = thin_border


        for col in worksheet.columns:
            max_length = 0
            column = col[0].column_letter 
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2)
            worksheet.column_dimensions[column].width = adjusted_width

        team_info = pd.DataFrame([
            ['Brian Ochoa', 'linkedin.com/in/brian-ochoa/'],
            ['Fabián Espitia', 'linkedin.com/in/fabian-espitia-sotelo/'],
            ['Sergio Rey', 'linkedin.com/in/rey-sergio/'],
            ['Julian Bolaños', 'linkedin.com/in/juliancbolanos/'],
            ['Manuel Romero', 'linkedin.com/in/manuelsantiagoromero/']
        ], columns=['Development Team', 'LinkedIn'])

        team_info.to_excel(writer, index=False, sheet_name='Development Team')

        team_sheet = writer.sheets['Development Team']

        #Team border
        for row in team_sheet.iter_rows(min_row=1, max_row=6, min_col=1, max_col=2):
            for cell in row:
                cell.border = thin_border

        
        for col in team_sheet.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2)
            team_sheet.column_dimensions[column].width = adjusted_width

    buffer.seek(0)

    return StreamingResponse(buffer, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment;filename=favorite_funds.xlsx"})


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

    df = pd.DataFrame([startup.__dict__ for startup in favorite_startups])
    df = df.drop(columns=['_sa_instance_state', 'id', 'photo'])

    df = map_ids_to_names(db, df, 'country_id', Country, 'name')
    df = map_ids_to_names(db, df, 'sector_id', Sector, 'name')
    df = map_ids_to_names(db, df, 'round_id', Round, 'stage')
    df = map_ids_to_names(db, df, 'traction_id', Traction, 'name')


    df = df[['name', 'email', 'linkedin', 'description', 'fund_raised', 'website', 'phone_number', 'calendly', 'one_sentence_description', 'deck', 'country', 'sector', 'round', 'traction']]

    
    empty_row = pd.DataFrame([[''] * len(df.columns)], columns=df.columns)

    startups_title = pd.DataFrame([['Your_Favorite_Startups'] + [''] * (len(df.columns) - 1)], columns=df.columns)

 
    df = pd.concat([empty_row, startups_title, pd.DataFrame([df.columns], columns=df.columns), df], ignore_index=True)

    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, header=False)
        worksheet = writer.sheets['Sheet1']

        for cell in worksheet["A2:N2"]:
            for c in cell:
                c.font = Font(bold=True)

        thin_border = Border(left=Side(style='thin'), 
                             right=Side(style='thin'), 
                             top=Side(style='thin'), 
                             bottom=Side(style='thin'))

        worksheet['A2'].font = Font(bold=True)

        #Your Favorite Startups Border
        worksheet['A2'].border = thin_border

        for cell in worksheet["A3:N3"]:
            for c in cell:
                c.font = Font(bold=True)
        
        
        end_row = 3 + len(favorite_startups)

        #Startup informarion border
        for row in worksheet.iter_rows(min_row=3, max_row=end_row, min_col=1, max_col=worksheet.max_column):
            for cell in row:
                cell.border = thin_border
    
        

        for col in worksheet.columns:
            max_length = 0
            column = col[0].column_letter 
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2)
            worksheet.column_dimensions[column].width = adjusted_width
        
        team_info = pd.DataFrame([
            ['Brian Ochoa', 'linkedin.com/in/brian-ochoa/'],
            ['Fabián Espitia', 'linkedin.com/in/fabian-espitia-sotelo/'],
            ['Sergio Rey', 'linkedin.com/in/rey-sergio/'],
            ['Julian Bolaños', 'linkedin.com/in/juliancbolanos/'],
            ['Manuel Romero', 'linkedin.com/in/manuelsantiagoromero/']
        ], columns=['Development Team', 'LinkedIn'])

        team_info.to_excel(writer, index=False, sheet_name='Development Team')

        team_sheet = writer.sheets['Development Team']

        #Team border
        for row in team_sheet.iter_rows(min_row=1, max_row=6, min_col=1, max_col=2):
            for cell in row:
                cell.border = thin_border

        
        for col in team_sheet.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2)
            team_sheet.column_dimensions[column].width = adjusted_width

    buffer.seek(0)

    return StreamingResponse(buffer, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment;filename=favorite_startups.xlsx"})

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


@user.put("/user/startup/bulk", tags=["users"])
def add_user_startups_bulk(background_tasks: BackgroundTasks, db: Session = Depends(get_db), user_data: UserStartup = None) -> JSONResponse:
    background_tasks.add_task(create_user_startup_new, db=db, user_data=user_data)
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


@user.post("/user/add_normal_user", tags=["users"])
def add_normal_user(background_tasks: BackgroundTasks, user_data: UserNormal, db: Session = Depends(get_db)):

    background_tasks.add_task(create_normal_user, db=db, user_data = user_data)
    return JSONResponse(content={"response": "created"}, status_code=status.HTTP_201_CREATED)


    

@user.put("/user/attendee_user", tags=["users"])
def add_attendee_user(background_tasks: BackgroundTasks, user_data: UserAttendee, db: Session = Depends(get_db)):

    background_tasks.add_task(create_attendee_user, db=db, user_data = user_data)
    return JSONResponse(content={"response": "created"}, status_code=status.HTTP_201_CREATED)
    


@user.put("/user/investor_user", tags=["users"])
def add_investor_user(background_tasks: BackgroundTasks,user_data: UserInvestor, db: Session = Depends(get_db)):
    background_tasks.add_task(create_investor_user, db=db, user_data = user_data)
    return JSONResponse(content={"response": "created"}, status_code=status.HTTP_201_CREATED)

