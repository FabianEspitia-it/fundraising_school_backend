import os
#import magic

from fastapi import APIRouter, HTTPException, status, Depends, File, UploadFile
from fastapi.responses import JSONResponse

from src.database import get_db
from src.startups.crud import *

from src.startups.schemas import NewStartupReq, UpdateStartupReq, CreateBulkStartupReq


startup_router = APIRouter()


# STARTUPS ROUTES


@startup_router.get("/startups/all", tags=["startups"])
def get_startups(db: Session = Depends(get_db), page: int = 1, limit: int = 10, user_email: str = None, country: str | None = None, sector: str | None = None, traction: str | None = None, startup_term: str | None = None):
    """
    Retrieve a list of startups.

    Args:
        db (Session, optional): Database session dependency.
        page (int, optional): The page number for pagination. Defaults to 0.
        limit (int, optional): The number of records to return per page. Defaults to 10.

    Returns:
        JSONResponse: A JSON response containing the list of startups.
    """

    if not user_email:
        return HTTPException(status_code=400, detail="Not User")

    if page <= 0:
        page = 1

    return dict(page=page, total=total_startups(db, country=country, sector=sector, traction=traction, term=startup_term), data=get_all_startups(db=db, page=page, limit=limit, user_email=user_email, country=country, sector=sector, traction=traction, term=startup_term))


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


@startup_router.get("/startups/filter/options", tags=["startups"])
def get_filter_options(db: Session = Depends(get_db)):

    countries: list[str] = []
    countries_db = get_countries(db=db)
    startup_countries = get_country_startups(db=db)

    startup_country_ids = [country_id for (country_id,) in startup_countries]

    for country in countries_db:
        if country.id in startup_country_ids:
            countries.append(country.name)

    sectors: list[str] = []
    sectors_db = get_sectors(db=db)
    startup_sectors = get_sector_startups(db=db)

    startup_sectors_ids = [sector_id for (sector_id,) in startup_sectors]

    for sector in sectors_db:
        if sector.id in startup_sectors_ids:
            sectors.append(sector.name)

    tractions: list[str] = []
    tractions_db = get_tractions(db=db)
    startup_tractions = get_traction_startups(db=db)

    startup_tractions_ids = [traction_id for (
        traction_id,) in startup_tractions]
    for traction in tractions_db:
        if traction.id in startup_tractions_ids:
            tractions.append(traction.name)

    return dict(countries=countries, sectors=sectors, tractions=tractions)


@startup_router.get("/startup/countries", tags=["startups"])
def get_countries_startups(db: Session = Depends(get_db)):
    return get_countries(db=db)


@startup_router.get("/startup/users/{startup_name}", tags=["startups"])
def get_startup_users(startup_name: str, db: Session = Depends(get_db)):
    return get_users_by_startup_name(db=db, startup_name=startup_name)


@startup_router.post("/startup/{startup_id}/startup_photo/", tags=["startups"])
async def gcs_upload_file(startup_id: int | None = None, startup_photo: UploadFile = File(...), db: Session = Depends(get_db)):

    content = await startup_photo.read()
    size = len(content)

    KB = 1024
    MB = 1024 * KB
    if not 0 < size <= 1 * MB:
        raise HTTPException(
            status_code=400,
            detail="Supported file sizes is 0 - 1 MB"
        )

    supported_image_types = SUPPORTED_IMAGES_TYPES

    file_type = magic.from_buffer(buffer=content, mime=True)
    if file_type not in supported_image_types:
        raise HTTPException(
            status_code=400,
            detail=f'Unsupported file type: {file_type}. Supported file types are: {supported_image_types.keys()}'
        )

    url = await gcs_upload(startup_photo, startup_id, file_type)
    update_startup_photo(db=db, startup_id=startup_id, startup_photo_link=url)

    return JSONResponse(content={"bucket_link": url}, status_code=status.HTTP_201_CREATED)
