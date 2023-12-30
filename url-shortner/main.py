from fastapi import FastAPI,HTTPException,Depends,Request
from fastapi import status
from fastapi.responses import RedirectResponse
from . import schemas,models,crud
import secrets
from pydantic import BaseModel,AnyHttpUrl,ValidationError
from .database import engine,SessionLocal
from sqlalchemy.orm import session
app=FastAPI()
models.Base.metadata.create_all(bind=engine)
BASE_URL = "http://localhost:8000"
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
@app.get("/")
def read():
    return "Hello I am url shortner.."
@app.post("/shorten",response_model=schemas.URLInfo)
def createurl(url:schemas.URLBase,db:session=Depends(get_db)):
    try:
        AnyHttpUrl(url.target_url)
    except ValidationError as e:
        raise HTTPException(status_code=400,detail="Please provide a valid url") from e
    key=secrets.token_urlsafe(5) 
    target_url_str=str(url.target_url)
    db_url=models.URL(target_url=target_url_str,key=key)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    complete_url = f"{BASE_URL}/{key}"
    db_url.url=complete_url
    return db_url
def raise_not_found(request):
    message = f"URL '{request.url}' doesn't exist"
    raise HTTPException(status_code=404, detail=message)
@app.get("/{url_key}",response_class=RedirectResponse)
def shorten_url(url_key:str,request:Request,db:session=Depends(get_db)):
    db_url=db.query(models.URL).filter(models.URL.key==url_key,models.URL.is_active).first()
    if db_url:
        return RedirectResponse(db_url.target_url)
    else:
        raise_not_found(request)

@app.delete("/{url_key}")
def delete_url(
    url_key: str, request: Request, db: session = Depends(get_db)
):
    if db_url := crud.deactivate_db_url_by_key(db, key=url_key):
        message = f"Successfully deleted shortened URL for '{db_url.target_url}'"
        return {"detail": message}
    else:
        raise_not_found(request)