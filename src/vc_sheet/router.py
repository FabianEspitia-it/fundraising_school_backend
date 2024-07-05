from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse

from src.database import get_db
from src.vc_sheet.crud import *
from src.vc_sheet.test import get_investor_info
from src.vc_sheet.vc_scraper import *

vc_sheet_router = APIRouter()

# FUND ROUTES

@vc_sheet_router.get("/vc_sheet/funds", tags=["vc_sheet"])
def get_funds(db: Session = Depends(get_db), page: int = 1, limit: int = 10, user_email: str | None = None, country: str | None = None, sector: str | None = None, check_size: str | None = None, fund_round: str | None = None):
    """
    Retrieve a list of venture capital funds.

    Args:
        db (Session, optional): Database session dependency.
        page (int, optional): The page number for pagination. Defaults to 0.
        limit (int, optional): The number of records to return per page. Defaults to 10.

    Returns:
        JSONResponse: A JSON response containing the list of funds.
    """
    return dict(page=page, total=total_funds(db, country, sector, check_size, fund_round), data=get_all_funds(db=db, page=page, limit=limit, user_email=user_email, country=country, sector=sector, check_size=check_size, round_op=fund_round))


@vc_sheet_router.get("/vc_sheet/filter/options", tags=["vc_sheet"])
def get_filter_options(db: Session = Depends(get_db)):
    """
    Retrieve the filter options for the venture capital funds.
    Args:
        db (Session, optional): Database session dependency.
    Returns:
        JSONResponse: A JSON response containing the filter options.
    """
    countries: list[str] = []
    countries_db = get_countries(db=db)
    for country in countries_db:
        countries.append(country.name)


    sectors: list[str] = []
    sectors_db = get_sectors(db=db)
    for sector in sectors_db:
        sectors.append(sector.name)

    check_size: list[str] = []
    check_size_db = get_check_sizes(db=db)
    for size in check_size_db:
        check_size.append(size.size)

    rounds: list[str] = []
    rounds_db = get_rounds(db=db)
    for round in rounds_db:
        rounds.append(round.stage)    

    return dict(countries=countries, sectors=sectors, check_size=check_size, rounds=rounds)

@vc_sheet_router.get("/vc_sheet/funds/{fund_id}", tags=["vc_sheet"])
def get_fund(fund_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific venture capital fund.

    Args:
        fund_id (int): The unique identifier of the fund.
        db (Session, optional): Database session dependency.

    Returns:
        JSONResponse: A JSON response containing the fund information.

    Raises:
        HTTPException: If the fund does not exist (status code 404).
    
    """
    fund = get_fund_by_id(db=db, fund_id=fund_id)

    if not fund:
        raise HTTPException(status_code=404, detail="Fund not found")

    return fund


@vc_sheet_router.post("/vc_sheet/funds/add", tags=["vc_sheet"])
def new_fund(db: Session = Depends(get_db)) -> JSONResponse:
    """
    Scrape and add new venture capital funds to the database.

    Args:
        db (Session, optional): Database session dependency.

    Returns:
        JSONResponse: A JSON response indicating the creation status.
    """
    funds, final_fund_invest, fund_sectors, fund_countries_invest, check_size_range, partner_names, partner_links = vc_scraper_funds()

    create_bulk_fund(
        db=db, 
        funds=funds,
        fund_rounds=final_fund_invest,
        fund_countries=fund_countries_invest,
        fund_partners=partner_names,
        fund_check_size=check_size_range,
        fund_sectors=fund_sectors,
        partner_links=partner_links

    ) 

    return JSONResponse(content={"response": "created"}, status_code=status.HTTP_201_CREATED)


#PARTNER ROUTES


@vc_sheet_router.post("/vc_sheet/partners/add", tags=["vc_sheet"])
def new_partner(db: Session = Depends(get_db)) -> JSONResponse:
    """
    Add new partner information to the database.

    Args:
        db (Session, optional): Database session dependency.

    Returns:
        JSONResponse: A JSON response indicating the creation status.
    """
    add_partners_information(db=db)

    return JSONResponse(content={"response": "created"}, status_code=status.HTTP_201_CREATED)


@vc_sheet_router.get("/vc_sheet/partners/{partner_id}", tags=["vc_sheet"])
def get_partner(partner_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific partner.

    Args:
        partner_id (int): The unique identifier of the partner.
        db (Session, optional): Database session dependency.

    Returns:
        JSONResponse: A JSON response containing the partner information.

    Raises:
        HTTPException: If the partner does not exist (status code 404).
    """
    partner = get_partner_by_id(db=db, partner_id=partner_id)

    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")

    return partner


@vc_sheet_router.post("/vc_sheet/crm_investors", tags=["vc_sheet"])
def new_investor(db: Session = Depends(get_db)) -> JSONResponse:
    """
    Scrape and add new investors to the database.

    Args:
        db (Session, optional): Database session dependency.

    Returns:
        JSONResponse: A JSON response indicating the creation status.
    """
    investors = get_investor_info()

    create_bulk_crm_investors(db=db, crm_investors=investors)

    return JSONResponse(content={"response": "created"}, status_code=status.HTTP_201_CREATED)


"""
ROUTES THAT WE DONT NEED AT THE MOMENT

@vc_sheet_router.post("/reporters/", tags=["vc_sheet"])
def new_reporter(db: Session = Depends(get_db)) -> JSONResponse:
    reporters = vc_scraper_reporters()

    create_bulk_reporters(db=db, reporters=reporters)

    return JSONResponse(content={"response": "created"}, status_code=status.HTTP_201_CREATED)


@vc_sheet_router.get("/vc_sheet/reporters", tags=["vc_sheet"])
def get_reporters(db: Session = Depends(get_db), page: int = 0, limit: int = 10):
    return pagination_reporters(db=db, page=page, limit=limit)


# Investor Routes

@vc_sheet_router.post("/investors/", tags=["vc_sheet"])
def new_investor(db: Session = Depends(get_db)) -> JSONResponse:
    investors, invest = vc_scraper_investors()

    create_bulk_investors(db=db, investors=investors, investor_rounds=invest)

    return JSONResponse(content={"response": "created"}, status_code=status.HTTP_201_CREATED)


@vc_sheet_router.get("/vc_sheet/investors", tags=["vc_sheet"])
def get_investors(db: Session = Depends(get_db), page: int = 0, limit: int = 10):
    return get_all_investors(db=db, page=page, limit=limit)

"""




