import os
import requests
from sqlalchemy import func
import pandas as pd
from requests import Session
import warnings
warnings.filterwarnings('ignore')


from src.database import get_db
from src.models import CheckSize, Country, Fund, FundCheckSize, FundCountry, FundRound, FundSector, FundUsers, Round, Sector, Startup, StartupUser, User, Course, Partner, FundPartner

from google.cloud import storage
from google.oauth2 import service_account


PARTNERS_FILE = 'src/partners_ctw.xlsx'


def upload_image_to_gcs(image_path: str):
    bucket_name = os.getenv('GCS_BUCKET_NAME')
    
    credentials = service_account.Credentials.from_service_account_file(
        os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    )
    client = storage.Client(credentials=credentials)

    bucket = client.bucket(bucket_name)
    blob = bucket.blob(f'partners/{image_path.split('/')[-1]}')

    blob.upload_from_filename(image_path)

    return blob.public_url


def download_image(drive_url: str, partner_id: int):
    os.makedirs(os.path.dirname('./partners'), exist_ok=True)
    image_path = f'{os.getcwd()}/partners/{partner_id}.png'
    file_id = drive_url.split('/d/')[1].split('/')[0]
    download_url = f"https://drive.google.com/uc?id={file_id}&export=download"

    response = requests.get(download_url, stream=True)

    if response.status_code == 200:
        with open(image_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)

    return image_path


def execute_image_load(db: Session):
    df = pd.read_excel(PARTNERS_FILE)
    
    df_parternsA = df[['Representante 1 ', 'Foto']]
    df_parternsB = df[['Representante 2', 'Foto 2']]
    df_partnersC = df[['Representante 3', 'Foto 3']]

    df_parternsA.rename(columns={'Representante 1 ': 'Representante'}, inplace=True)
    df_parternsB.rename(columns={'Representante 2': 'Representante', 'Foto 2': 'Foto'}, inplace=True)
    df_partnersC.rename(columns={'Representante 3': 'Representante', 'Foto 3': 'Foto'}, inplace=True)

    df = pd.concat([df_parternsA, df_parternsB])
    df.dropna(inplace=True)
    df = df[df['Foto'].str.contains(r'\bhttps\b')]

    for _, row in df.iterrows():

        partner = db.query(Partner).filter(func.lower(func.trim(Partner.name)) == func.lower(row["Representante"].strip())).first()
        if partner:
            partner_id = partner.id
            image_path = download_image(
                row['Foto'], 
                partner_id
                )
            partner_image_url = upload_image_to_gcs(image_path)
            
            db.query(Partner).filter(func.lower(func.trim(Partner.name)) == func.lower(row["Representante"].strip())
                                ).update({'photo': partner_image_url})
            db.commit()
            print(f'Partner {partner_id} image uploaded.')
        else:
            print(f'Partner {row["Representante"]} not founded in DB')


if __name__ == '__main__':
    db_session = next(get_db())
    execute_image_load(db_session)
    