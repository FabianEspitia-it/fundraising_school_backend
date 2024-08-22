import pandas as pd
from requests import Session
from sqlalchemy import func

from src.database import get_db
from src.models import  Fund,  FundPartner,  Partner


def process_excel(file_path: str, db: Session):
    df = pd.read_excel(file_path, header=0)
    print(df.columns)

    for _, row in df.iterrows():
        if row["Batch"] == "S1":
            if pd.notna(row["Representante 1 "]):
                partner = Partner(
                    name=row["Representante 1 "],
                    photo=row["Foto"] if pd.notna(row["Foto"]) else None,
                    role=row["Cargo"] if pd.notna(row["Cargo"]) else None,
                    email=row["Correo"] if pd.notna(row["Correo"]) else None,
                    linkedin=row["LinkedIn"] if pd.notna(row["LinkedIn"]) else None,
                )

                db.add(partner)
                db.commit()
                db.refresh(partner)

                fund = db.query(Fund).filter(func.lower(Fund.name) == func.lower(row["Nombre Fondo"].strip())).first()

                if fund is None:
                    print(f"Fondo no encontrado: {row['Nombre Fondo']}")
                    continue

                user_fund = FundPartner(
                    fund_id=fund.id,
                    partner_id=partner.id
                )

                db.add(user_fund)
                db.commit()
                db.refresh(user_fund)

            if pd.notna(row["Representante 2"]):
                partner_2 = Partner(
                    name=row["Representante 2"],
                    photo=row["Foto 2"] if pd.notna(row["Foto 2"]) else None,
                    role=row["Cargo 2"] if pd.notna(row["Cargo 2"]) else None,
                    email=row["Correo 2"] if pd.notna(row["Correo 2"]) else None,
                    linkedin=row["LinkedIn 2"] if pd.notna(row["LinkedIn 2"]) else None,
                )

                db.add(partner_2)
                db.commit()
                db.refresh(partner_2)

                if fund is None:
                    print(f"Fondo no encontrado: {row['Nombre Fondo']}")
                    continue

                user_fund_two = FundPartner(
                    fund_id=fund.id,
                    partner_id=partner_2.id
                )

                db.add(user_fund_two)
                db.commit()
                db.refresh(user_fund_two)
        

db_session = next(get_db())  
process_excel("src/partners_ctw.xlsx", db_session)
