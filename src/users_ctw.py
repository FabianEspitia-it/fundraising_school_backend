import pandas as pd
from requests import Session

from src.database import get_db
from src.models import Fund, FundUsers, Startup, StartupUser, User, Course


def process_excel(file_path: str, db: Session):
    df = pd.read_excel(file_path, header=0)
    print(df.columns)

    ctw_fund = Fund(
        name="CTW Fund",

    )

    db.add(ctw_fund)
    db.commit()
    db.refresh(ctw_fund)

    for _, row in df.iterrows():
        user_type = row["Tipo de Usuario"]
        if user_type != "Investor" and user_type != "Entrepreneur":
          
            if pd.notna(row["Email"]):
                user_email = db.query(User).filter(User.email == row["Email"]).first()
            else:
                user_email = None

            if pd.notna(row["LinkedIn"]):
                user_linkedin = db.query(User).filter(User.linkedin_url == row["LinkedIn"]).first()
            else:
                user_linkedin = None

            if user_email or user_linkedin:
                print("User already exists")
            else:
                user_data = User(
                    first_name=row["Nombre"] if pd.notna(row["Nombre"]) else None,
                    last_name=row["Apellido"] if pd.notna(row["Apellido"]) else None,
                    email=row["Email"] if pd.notna(row["Email"]) else None,
                    country_code=row["Código País"] if pd.notna(row["Código País"]) else None,
                    phone_number=str(row["Whatsapp ( solo el numero)"]).replace(" ", "").replace("-", "") if pd.notna(row["Whatsapp ( solo el numero)"]) else None,
                    location=row["País de residencia"] if pd.notna(row["País de residencia"]) else None,
                    linkedin_url=row["LinkedIn"] if pd.notna(row["LinkedIn"]) and len(str(row["LinkedIn"])) <= 255 else None,
                    courses=db.query(Course).all()
                )
                db.add(user_data)
                db.commit()
                db.refresh(user_data)

        elif user_type == "Investor":

            if pd.notna(row["Email"]):
                user_email = db.query(User).filter(User.email == row["Email"]).first()
            else:
                continue

            if pd.notna(row["LinkedIn"]):
                user_linkedin = db.query(User).filter(User.linkedin_url == row["LinkedIn"]).first()
            else:
                user_linkedin = None

            if user_email or user_linkedin:
                print("User already exists")
            else:
                user_data = User(
                    first_name=row["Nombre"] if pd.notna(row["Nombre"]) else None,
                    last_name=row["Apellido"] if pd.notna(row["Apellido"]) else None,
                    email=row["Email"] if pd.notna(row["Email"]) else None,
                    country_code=row["Código País"] if pd.notna(row["Código País"]) else None,
                    phone_number=str(row["Whatsapp ( solo el numero)"]).replace(" ", "").replace("-", "") if pd.notna(row["Whatsapp ( solo el numero)"]) else None,
                    location=row["País de residencia"] if pd.notna(row["País de residencia"]) else None,
                    linkedin_url=row["LinkedIn"] if pd.notna(row["LinkedIn"]) and len(str(row["LinkedIn"])) <= 255 else None,
                    investment_stage=row["Investment Stage (con multiples opciones desplegables)"] if pd.notna(row["Investment Stage (con multiples opciones desplegables)"]) else None,
                    investment_geography=row["Investment Geography (con multiples opciones desplegables maximo 3)"] if pd.notna(row["Investment Geography (con multiples opciones desplegables maximo 3)"]) else None,
                    industry_to_invest=row["Industry to Invest (con multiples opciones desplegables)"] if pd.notna(row["Industry to Invest (con multiples opciones desplegables)"]) else None,
                    check_size=row["Tamaño de Ticket (Desplegable por rangos):"] if pd.notna(row["Tamaño de Ticket (Desplegable por rangos):"]) else None,
                    courses=db.query(Course).all()
                )
                db.add(user_data)
                db.commit()
                db.refresh(user_data)

                investor_ctw_fund = FundUsers(
                    user_id=user_data.id,
                    fund_id=ctw_fund.id
                )
                db.add(investor_ctw_fund)
                db.commit()


        elif user_type == "Entrepreneur":
            if pd.notna(row["Email"]):
                user_email = db.query(User).filter(User.email == row["Email"]).first()
            else:
                continue

            if pd.notna(row["LinkedIn"]):
                user_linkedin = db.query(User).filter(User.linkedin_url == row["LinkedIn"]).first()
            else:
                user_linkedin = None

            if user_email or user_linkedin:
                print("User already exists")

            else:
                
                user_data = User(
                    first_name=row["Nombre"] if pd.notna(row["Nombre"]) else None,
                    last_name=row["Apellido"] if pd.notna(row["Apellido"]) else None,
                    email=row["Email"] if pd.notna(row["Email"]) else "",
                    country_code=row["Código País"] if pd.notna(row["Código País"]) else None,
                    phone_number=str(row["Whatsapp ( solo el numero)"]).replace(" ", "").replace("-", "") if pd.notna(row["Whatsapp ( solo el numero)"]) else None,
                    location=row["País de residencia"] if pd.notna(row["País de residencia"]) else None,
                    linkedin_url=row["LinkedIn"] if pd.notna(row["LinkedIn"]) and len(str(row["LinkedIn"])) <= 255 else None,
                    startup_url=row["Startup URL"] if pd.notna(row["Startup URL"]) else None,
                    main_industry=row["Main Industry (con opciones desplegables)"] if pd.notna(row["Main Industry (con opciones desplegables)"]) else None,
                    role=row["Job Title"] if pd.notna(row["Job Title"]) else None,
                    courses=db.query(Course).all()
                )
                db.add(user_data)
                db.commit()
                db.refresh(user_data)

                startup = db.query(Startup).filter(Startup.name == str(row["Company/Fund Name"]).title()).first()
                if not startup:
                    startup = Startup(name=str(row["Company/Fund Name"]).title())
                    db.add(startup)
                    db.commit()
                    db.refresh(startup)

                    startup_user = StartupUser(
                        user_id=user_data.id,
                        startup_id=startup.id
                    )
                    db.add(startup_user)
                    db.commit()
                else:
                    startup_user = StartupUser(
                        user_id=user_data.id,
                        startup_id=startup.id
                    )
                    db.add(startup_user)
                    db.commit()
                    db.refresh(startup_user)
           

        print("User Added")
    
    
db_session = next(get_db())  
process_excel(file_path="src/datos_final.xlsx", db=db_session)

