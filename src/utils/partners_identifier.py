from src.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from src.models import Fund, FundPartner, Partner

import hashlib


def generate_partner_identifier(db: Session):
        partners = db.query(Partner).all()
        
        for partner in partners:
            hash_object = hashlib.sha256()
            hash_object.update(partner.email.encode('utf-8') if partner.email else b'')
            hash_hex = hash_object.hexdigest()
            
            partner.partner_identifier = hash_hex

            try:
                db.add(partner)
                db.commit()

            except SQLAlchemyError as e:
                db.rollback()
                print(e)

        return "Identifiers generated successfully"
        
        
    

db_session = next(get_db())  
print(generate_partner_identifier(db_session))
