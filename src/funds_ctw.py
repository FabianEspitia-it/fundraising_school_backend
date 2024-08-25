import pandas as pd
from requests import Session
import sqlalchemy

from sqlalchemy import func

from src.database import get_db
from src.models import CheckSize, Country, Fund, FundCheckSize, FundCountry, FundRound, FundSector, FundUsers, Round, Sector, Startup, StartupUser, User, Course



def checker(db: Session, model, model_two, fund_id: int, model_id_attr: str, **kwargs):

    instance = db.query(model).filter_by(**kwargs).first()

    if not instance:
      
        instance = model(**kwargs)
        db.add(instance)
        db.commit()
        db.refresh(instance)

    
    instance_two = model_two(
        fund_id=fund_id,
        **{model_id_attr: instance.id}
    )

    
    db.add(instance_two)
    db.commit()
    db.refresh(instance_two)

   

def process_excel(file_path: str, db: Session):
    df = pd.read_excel(file_path, header=0)
    print(df.columns)
    
    for _, row in df.iterrows():
        try:
            if pd.notna(row["Limpieza"]):
                fund = db.query(Fund).filter(func.lower(Fund.name) == func.lower(row["Investors"].strip())).first()
                if not fund:
                    fund = Fund(
                        name = row["Investors"] if pd.notna(row["Investors"]) else None,
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
                        checker(db=db, model=Round, model_two=FundRound, fund_id=fund.id, model_id_attr='round_id', stage=round)

                    countries = [c.strip() for c in str(row["Geografías en las que invierten"]).split(",")]
                    for country in countries:
                        checker(db=db, model=Country, model_two=FundCountry, fund_id=fund.id, model_id_attr='country_id', name=country[:255])
                        
                    sectors = [s.strip() for s in str(row["Sectores en los que invierten"]).split(",")]
                    for sector in sectors:
                        checker(db=db, model=Sector, model_two=FundSector, fund_id=fund.id, model_id_attr='sector_id', name=sector[:255])

                    check_sizes = [s.strip() for s in str(row["Rango de tamaño del cheque"]).split(",")]
                    for check_size in check_sizes:
                        checker(db=db, model=CheckSize, model_two=FundCheckSize, fund_id=fund.id, model_id_attr='check_size_id', size=check_size)

                    print("Fund added")
                else:
                    continue
            else:
                print(f"Fund not done: {row['Investors']}")

        except sqlalchemy.exc.DataError as e:
                db.rollback()  
                print(f"Error al agregar el inversor {row['Investors']}: {e}")
        except Exception as e:
                db.rollback() 
                print(f"Error desconocido al agregar el inversor {row['Investors']}: {e}")

                    
        



db_session = next(get_db())  
process_excel("src/funds_ctw.xlsx", db_session)