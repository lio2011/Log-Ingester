from db import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship

class Logs(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True,nullable=False)
    level = Column(String,nullable=False)
    message = Column(String,nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True),nullable = False)
    traceId = Column(String,nullable=False)
    spanId = Column(String,nullable=False)
    extra_fields = Column(JSON, nullable=True)
