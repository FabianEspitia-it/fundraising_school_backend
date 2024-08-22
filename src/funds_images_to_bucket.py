import os
import requests
import sqlalchemy
import pandas as pd
from requests import Session
import warnings
warnings.filterwarnings('ignore')


from src.database import get_db
from src.models import CheckSize, Country, Fund, FundCheckSize, FundCountry, FundRound, FundSector, FundUsers, Round, Sector, Startup, StartupUser, User, Course

from google.cloud import storage
from google.oauth2 import service_account


FUNDS_FILE = 'src/funds_ctw.xlsx'


def upload_image_to_gcs(image_path: str):
    bucket_name = os.getenv('GCS_BUCKET_NAME')
    
    credentials = service_account.Credentials.from_service_account_file(
        os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    )
    client = storage.Client(credentials=credentials)

    bucket = client.bucket(bucket_name)
    blob = bucket.blob(f'funds/{image_path.split('/')[-1]}')

    blob.upload_from_filename(image_path)

    return blob.public_url


def download_image(drive_url: str, fund_id: int):
    os.makedirs(os.path.dirname('./funds'), exist_ok=True)
    image_path = f'{os.getcwd()}/funds/{fund_id}.png'
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
    df = pd.read_excel(FUNDS_FILE)
    df = df[df['Batch'] == 'S1']
    df = df[['Investors', 'Logo (de me lleve a la imagen)']]
    df = df[df['Logo (de me lleve a la imagen)'].str.contains(r'\bhttps\b')]

    for _, row in df.iterrows():
        image_path = download_image(
            row['Logo (de me lleve a la imagen)'], 
            db.query(Fund).filter(Fund.name == row["Investors"]).first().id
            )
        fund_image_url = upload_image_to_gcs(image_path)
        
        db.query(Fund).filter(Fund.name == row["Investors"]
                              ).update({'photo': fund_image_url})
        db.commit()


if __name__ == '__main__':
    db_session = next(get_db())
    execute_image_load(db_session)
    