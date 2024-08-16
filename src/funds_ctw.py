import pandas as pd
from requests import Session

from src.database import get_db
from src.models import CheckSize, Country, Fund, FundCheckSize, FundCountry, FundRound, FundSector, FundUsers, Round, Sector, Startup, StartupUser, User, Course


def process_excel(file_path: str, db: Session):
    df = pd.read_excel(file_path, header=0)
    print(df.columns)

    for _, row in df.iterrows():
        fund = Fund(
            name = row["Nombre Fondo"] if pd.notna(row["Nombre Fondo"]) else None,
            description = row["Descripción: [Tesis de inversión del fondo]"] if pd.notna(row["Descripción: [Tesis de inversión del fondo]"]) else None,
            photo = row["Logo (de me lleve a la imagen)"] if pd.notna(row["Logo (de me lleve a la imagen)"]) else None,
            website = row["URL del Fondo: [Ingrese la URL]"] if pd.notna(row["URL del Fondo: [Ingrese la URL]"]) else None,
            twitter = row["Twitter: [Ingrese el enlace de Twitter]"] if pd.notna(row["Twitter: [Ingrese el enlace de Twitter]"]) else None,
            linkedin = row["LinkedIn"] if pd.notna(row["LinkedIn"]) else None,
            crunch_base = row["Crunchbase: [Ingrese el enlace de Crunchbase]"] if pd.notna(row["Crunchbase: [Ingrese el enlace de Crunchbase]"]) else None,
            contact = row["Contacto Preferido: Email - enlace de formulario etc."] if pd.notna(row["Contacto Preferido: Email - enlace de formulario etc."]) else None,

        )

        db.add(fund)
        db.commit()
        db.refresh(fund)
        
        rounds = [r.strip() for r in str(row["Rondas en las que invierten"]).split(",")]
        for round in rounds: 
            round_checker = db.query(Round).filter(Round.stage == round).first()

            if not round_checker:
                round_data = Round(
                    stage = round
                )
                db.add(round_data)
                db.commit()
                db.refresh(round_data)

                fund_round = FundRound(
                    fund_id = fund.id,
                    round_id = round_data.id
                )

                db.add(fund_round)
                db.commit()
                db.refresh(fund_round)
            else:
                fund_round = FundRound(
                    fund_id = fund.id,
                    round_id = round_checker.id
                )

                db.add(fund_round)
                db.commit()
                db.refresh(fund_round)

        countries = [c.strip() for c in str(row["Geografías en las que invierten"]).split(",")]
        for country in countries:
            country_checker = db.query(Country).filter(Country.name == country).first()

            if not country_checker:
                country_data = Country(
                    name = country
                )
                db.add(country_data)
                db.commit()
                db.refresh(country_data)

                fund_country = FundCountry(
                    fund_id = fund.id,
                    country_id = country_data.id
                )

                db.add(fund_country)
                db.commit()
                db.refresh(fund_country)
            else:
                fund_country = FundCountry(
                    fund_id = fund.id,
                    country_id = country_checker.id
                )

                db.add(fund_country)
                db.commit()
                db.refresh(fund_country)

        sectors = [s.strip() for s in str(row["Sectores en los que invierten"]).split(",")]
        for sector in sectors:
            sector_checker = db.query(Sector).filter(Sector.name == sector).first()

            if not sector_checker:
                sector_data = Sector(
                    name = sector
                )
                db.add(sector_data)
                db.commit()
                db.refresh(sector_data)

                fund_sector = FundSector(
                    fund_id = fund.id,
                    sector_id = sector_data.id
                )

                db.add(fund_sector)
                db.commit()
                db.refresh(fund_sector)
            else:
                fund_sector = FundSector(
                    fund_id = fund.id,
                    sector_id = sector_checker.id
                )

                db.add(fund_sector)
                db.commit()
                db.refresh(fund_sector)

        check_sizes = [s.strip() for s in str(row["Rango de tamaño del cheque"]).split(",")]
        for check_size in check_sizes:
            check_size_check = db.query(CheckSize).filter(CheckSize.size == check_size).first()
            if not check_size_check:
                check_size = CheckSize(
                    size = check_size
                )

                db.add(check_size)
                db.commit()
                db.refresh(check_size)

                fund_check_size = FundCheckSize(
                    fund_id = fund.id,
                    check_size_id = check_size.id
                )

                db.add(fund_check_size)
                db.commit()
                db.refresh(fund_check_size)
            else:
                fund_check_size = FundCheckSize(
                    fund_id = fund.id,
                    check_size_id = check_size_check.id
                )

                db.add(fund_check_size)
                db.commit()
                db.refresh(fund_check_size)

        print("Fund added")  
        



db_session = next(get_db())  
process_excel("src/funds_ctw.xlsx", db_session)