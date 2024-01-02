import models
from sqlalchemy.orm import session
def get_db_url_by_key(db: session, key: str) -> models.URL:
    return (
        db.query(models.URL)
        .filter(models.URL.key == key,models.URL.is_active)
        .first()
    )
def deactivate_db_url_by_key(db: session, key: str):
    with db.begin():
        db_url = db.query(models.URL).filter(models.URL.key == key).first()
        if db_url:
            db_url.is_active = False
            # db.commit()
            # db.refresh(db_url)
            return db_url
    return None
