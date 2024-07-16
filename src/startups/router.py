from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse

from src.database import get_db
from src.startups.crud import *

from src.startups.schemas import NewStartupReq, UpdateStartupReq, CreateBulkStartupReq


startup_router = APIRouter()

# STARTUPS ROUTES


@startup_router.get("/startups/all", tags=["startups"])
def get_startups(db: Session = Depends(get_db), page: int = 0, limit: int = 10, user_email: str = None):
    """
    Retrieve a list of startups.

    Args:
        db (Session, optional): Database session dependency.
        page (int, optional): The page number for pagination. Defaults to 0.
        limit (int, optional): The number of records to return per page. Defaults to 10.

    Returns:
        JSONResponse: A JSON response containing the list of startups.
    """

    return get_all_startups(db=db, page=page, limit=limit, user_email=user_email)


@startup_router.get("/startups/{startup_id}", tags=["startups"])
def get_startup(startup_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific startup.

    Args:
        startup_id (int): The unique identifier of the startup.
        db (Session, optional): Database session dependency.

    Returns:

        JSONResponse: A JSON response containing the startup information.

    Raises:
        HTTPException: If the startup does not exist (status code 404).
    """

    startup = get_startup_by_id(db=db, startup_id=startup_id)

    if not startup:
        raise HTTPException(status_code=404, detail="Fund not found")

    return startup


@startup_router.post("/startups/add", tags=["startups"])
def add_startup(startup: NewStartupReq, db: Session = Depends(get_db)):
    """
    Add a new startup.

    Args:
        startup (StartupCreate): The startup information to add.
        db (Session, optional): Database session dependency.

    Returns:
        JSONResponse: A JSON response containing the newly added startup information.
    """

    create_startup(db=db, startup=startup)

    return JSONResponse(content={"response": "created"}, status_code=status.HTTP_201_CREATED)


@startup_router.patch("/startups/{startup_id}", tags=["startups"])
def update_startup(startup_id: int, startup: UpdateStartupReq, db: Session = Depends(get_db)):
    """
    Update a startup.

    Args:
        startup_id (int): The unique identifier of the startup.
        startup (NewStartupReq): The startup information to update.
        db (Session, optional): Database session dependency.

    Returns:
        JSONResponse: A JSON response containing the updated startup information.

    Raises:
        HTTPException: If the startup does not exist (status code 404).
    """

    updated_startup = update_startup_by_id(
        db=db, startup_id=startup_id, startup=startup)

    if not updated_startup:
        raise HTTPException(status_code=404, detail="Startup not found")

    return JSONResponse(content={"response": "updated"}, status_code=status.HTTP_200_OK)


@startup_router.post("/startups/bulk", tags=["startups"])
def add_bulk_startups(startups: list[CreateBulkStartupReq], db: Session = Depends(get_db)):
    """
    Add multiple startups.

    Args:
        startups (list[NewStartupReq]): The list of startup information to add.
        db (Session, optional): Database session dependency.

    Returns:
        JSONResponse: A JSON response containing the newly added startups information.
    """

    create_bulk_startup(db=db, startup_data_list=startups)

    return JSONResponse(content={"response": "created"}, status_code=status.HTTP_201_CREATED)
