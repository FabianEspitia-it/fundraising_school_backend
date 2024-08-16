import pandas as pd
from requests import Session

from src.database import get_db
from src.models import CheckSize, Country, Fund, FundCheckSize, FundCountry, FundPartner, FundRound, FundSector, FundUsers, Partner, Round, Sector, Startup, StartupUser, User, Course


def process_excel(file_path: str, db: Session):
    df = pd.read_excel(file_path, header=0)
    print(df.columns)

    for _, row in df.iterrows():
        partner = Partner(
            name = row["Representante 1"] if pd.notna(row["Representante 1"]) else None,
            photo = row["Foto"] if pd.notna(row["Foto"]) else None,
            role = row["Cargo"] if pd.notna(row["Cargo"]) else None,
            email = row["Correo"] if pd.notna(row["Correo"]) else None,
            linkedin = row["LinkedIn"] if pd.notna(row["LinkedIn"]) else None,

        )

        db.add(partner)
        db.commit()
        db.refresh(partner)

        fund = db.query(Fund).filter(Fund.name == row["Nombre Fondo"]).first()

        user_fund = FundPartner(
            fund_id = fund.id,
            partner_id = partner.id
        )

        db.add(user_fund)
        db.commit()
        db.refresh(user_fund)

        partern_2 = Partner(
            name = row["Representante 2"] if pd.notna(row["Representante 2"]) else None,
            photo = row["Foto 2"] if pd.notna(row["Foto 2"]) else None,
            role = row["Cargo 2"] if pd.notna(row["Cargo 2"]) else None,
            email = row["Correo 2"] if pd.notna(row["Correo 2"]) else None,
            linkedin = row["LinkedIn 2"] if pd.notna(row["LinkedIn 2"]) else None,

        )

        db.add(partern_2)
        db.commit()
        db.refresh(partern_2)

        user_fund_two = FundPartner(
            fund_id = fund.id,
            partner_id = partern_2.id
        )

        db.add(user_fund_two)
        db.commit()
        db.refresh(user_fund_two)

        
