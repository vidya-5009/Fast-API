from . database import Base
from sqlalchemy import Boolean,Column,Integer,String

class URL(Base):
    __tablename__="urls"
    id=Column(Integer,primary_key=True)
    key=Column(String,unique=True,index=True)
    target_url=Column(String,index=True)
    is_active=Column(Boolean,default=True)