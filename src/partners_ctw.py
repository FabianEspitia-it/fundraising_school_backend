import pandas as pd
from requests import Session
from sqlalchemy import func

from sqlalchemy.exc import SQLAlchemyError

from src.database import get_db
from src.models import  Fund,  FundPartner,  Partner



def process_excel(file_path: str, db: Session):
    df = pd.read_excel(file_path, header=0)
    print(df.columns)

    for _, row in df.iterrows():
        try:
            # Inicialización de variables
            partner = None
            partner_2 = None
            partner_3 = None

            # Búsqueda del fondo
            fund = db.query(Fund).filter(func.lower(func.trim(Fund.name)) == func.lower(row["Nombre Fondo"].strip())).first()
            if not fund:
                print(f"Fund '{row['Nombre Fondo']}' not found")
                continue

            # Procesar el primer representante
            try:
                if pd.notna(row["Representante 1 "]):
                    partner = db.query(Partner).filter(func.lower(func.trim(Partner.name)) == func.lower(row["Representante 1 "].strip())).first()
                    
                if not partner and pd.notna(row["Representante 1 "]):
                    partner = Partner(
                        name=row["Representante 1 "].strip(),
                        photo=row["Foto"] if pd.notna(row["Foto"]) else None,
                        role=row["Cargo"] if pd.notna(row["Cargo"]) else None,
                        email=row["Correo"] if pd.notna(row["Correo"]) else None,
                        linkedin=row["LinkedIn"] if pd.notna(row["LinkedIn"]) else None,
                    )
                    db.add(partner)
                    db.commit()
                    db.refresh(partner)

                    user_fund = FundPartner(
                        fund_id=fund.id,
                        partner_id=partner.id
                    )
                    db.add(user_fund)
                    db.commit()
                    db.refresh(user_fund)
                elif partner:
                    print("Partner already exists")
            
            except SQLAlchemyError as e:
                db.rollback()
                print(f"Database error processing 'Representante 1': {e}")
                continue
            
            # Procesar el segundo representante
            try:
                if pd.notna(row["Representante 2"]):
                    partner_2 = db.query(Partner).filter(func.lower(func.trim(Partner.name)) == func.lower(row["Representante 2"].strip())).first()

                if not partner_2 and pd.notna(row["Representante 2"]):
                    partner_2 = Partner(
                        name=row["Representante 2"].strip(),
                        photo=row["Foto 2"] if pd.notna(row["Foto 2"]) else None,
                        role=row["Cargo 2"] if pd.notna(row["Cargo 2"]) else None,
                        email=row["Correo 2"] if pd.notna(row["Correo 2"]) else None,
                        linkedin=row["LinkedIn 2"] if pd.notna(row["LinkedIn 2"]) else None,
                    )
                    db.add(partner_2)
                    db.commit()
                    db.refresh(partner_2)

                    user_fund_two = FundPartner(
                        fund_id=fund.id,
                        partner_id=partner_2.id
                    )
                    db.add(user_fund_two)
                    db.commit()
                    db.refresh(user_fund_two)
                elif partner_2:
                    print("Partner 2 already exists")

            except SQLAlchemyError as e:
                db.rollback()
                print(f"Database error processing 'Representante 2': {e}")
                continue

            # Procesar el tercer representante
            try:
                if pd.notna(row["Representante 3"]):
                    partner_3 = db.query(Partner).filter(func.lower(func.trim(Partner.name)) == func.lower(row["Representante 3"].strip())).first()

                if not partner_3 and pd.notna(row["Representante 3"]):
                    partner_3 = Partner(
                        name=row["Representante 3"].strip(),
                        photo=row["Foto 3"] if pd.notna(row["Foto 3"]) else None,
                        role=row["Cargo 3"] if pd.notna(row["Cargo 3"]) else None,
                        email=row["Correo 3"] if pd.notna(row["Correo 3"]) else None,
                        linkedin=row["LinkedIn 3"] if pd.notna(row["LinkedIn 3"]) else None,
                    )
                    db.add(partner_3)
                    db.commit()
                    db.refresh(partner_3)

                    user_fund_three = FundPartner(
                        fund_id=fund.id,
                        partner_id=partner_3.id
                    )
                    db.add(user_fund_three)
                    db.commit()
                    db.refresh(user_fund_three)
                elif partner_3:
                    print("Partner 3 already exists")

            except SQLAlchemyError as e:
                db.rollback()
                print(f"Database error processing 'Representante 3': {e}")
                continue

        except Exception as e:
            print(f"Unexpected error processing fund '{row['Nombre Fondo']}': {e}")
            continue


        

db_session = next(get_db())  
process_excel("src/partners_ctw.xlsx", db_session)
