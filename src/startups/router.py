from fastapi import APIRouter, HTTPException, status, Depends

from src.database import get_db
from src.startups.crud import *


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
