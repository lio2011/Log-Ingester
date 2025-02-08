from fastapi import FastAPI,Depends,HTTPException,Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Any,Dict
import schemas
import models
from sqlalchemy.orm import Session
from sqlalchemy import func
from db import get_db,engine
from datetime import datetime, timezone, timedelta
# from db import session,Logs
from elasticsearch import Elasticsearch
import logging
import os
# models.Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "http://elasticsearch:9200")
client = Elasticsearch([ELASTICSEARCH_HOST])

# client = Elasticsearch([{'host': 'localhost', 'port': 9200,'scheme' : 'http'}])

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4000"],  # Allow your frontend origin
    allow_credentials=True,
    allow_methods=["GET"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
async def root():
    return {"Message":"Backend Service is up and running"}


# async def store_log(log: schemas.Log, db: Session = Depends(get_db)):

#store logs
@app.post("/log")
async def store_log(log: schemas.Log):
    defined_fields = {column.name for column in models.Logs.__table__.columns}
    log_data = log.dict()
    known_fields = {key: value for key, value in log_data.items() if key in defined_fields}
    new_log = models.Logs(**known_fields)
    new_log.timestamp = datetime.now(timezone.utc)
    
    extra_fields = {key: value for key, value in log_data.items() if key not in defined_fields}
    for key, value in extra_fields.items():
        setattr(new_log, key, value)


    try:
        log_dict = {key: value for key, value in new_log.__dict__.items() if key != '_sa_instance_state'}
        # if not log_dict.get("extra_fields"):
        log_dict.pop("extra_fields", None)
        response = client.index(index="logs", document=log_dict, headers={"Authorization": "ApiKey bjJwQlA1UUJCbkdpMTg3VVFrOTk6aF85RG1EUDRSY0tNWE5wak9tVm9KQQ=="} )
        return {"message": "Log stored successfully", "log": new_log}
    except Exception as e:
        logger.error(f"Failed to store log: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to store log: {str(e)}")



# async def get_logs(db: Session = Depends(get_db), limit: int = 10):
    # logs = session.query(Logs).all()
    # results = db.query(models.Logs).limit(limit).all()

#get all logs
@app.get("/logs")
async def get_logs(size: int = 10):
    try:
        res = client.search(
            index="logs",
            body={
                "query": {
                    "match_all": {}
                },
                "size": size,
                "sort": [
                    {
                        "timestamp": {
                            "order": "desc"
                        }
                    }
                ]
            },
            headers={"Authorization": "ApiKey bjJwQlA1UUJCbkdpMTg3VVFrOTk6aF85RG1EUDRSY0tNWE5wak9tVm9KQQ=="}
        )
        return {"Count": res['hits']['total']['value'] ,"Response": res['hits']['hits']}
    except Exception as e:
        logger.error(f"Failed to retrieve logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve logs: {str(e)}")
        
#search logs
@app.get("/search")
async def search_logs(request: Request,message: str=None, size: int = 10, trace_id: str = None, span_id: str = None,level: str = None,time_frame: str = None):

    try:
        
        #pre processing
        query = {"query": {"bool": {"must": []}}}
        if trace_id:
            query["query"]["bool"]["must"].append({"match": {"traceId": trace_id}})
        if span_id:
            query["query"]["bool"]["must"].append({"match": {"spanId": span_id}})
        if message:
            query["query"]["bool"]["must"].append({"match": {"message": message}})
        if level:
            query["query"]["bool"]["must"].append({"match": {"level": level}})

        extra_fields = request.query_params
        for key, value in extra_fields.items():
            if key not in ["message", "size", "trace_id", "span_id", "level", "time_frame"]:
                query["query"]["bool"]["must"].append({"match": {key: value}})
        
        if time_frame:
            try:
                time_unit = time_frame[-1]
                time_value = int(time_frame[:-1])
                
                if time_unit == "h":
                    start_time = datetime.utcnow() - timedelta(hours=time_value)
                elif time_unit == "m":
                    start_time = datetime.utcnow() - timedelta(minutes=time_value)
                elif(time_unit == "d"):
                    start_time = datetime.utcnow() - timedelta(days=time_value)
                else:
                    raise ValueError("Unsupported time unit")
                query["query"]["bool"]["must"].append({
                "range": {
                    "timestamp": {
                        "gte": start_time.isoformat() + "Z",  # ISO8601 format
                        "lte": "now"  # Current time
                    }
                    }
                })
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid time format: {str(e)}")
        if not query["query"]["bool"]["must"]:
            return {"message": "No search criteria provided"}
        # actual search
        res = client.search(
            index="logs",
            body={
                "query":query["query"],
                "size": size,
                "sort": [{"timestamp": {"order": "desc"}}]
            },
            headers={"Authorization": "ApiKey bjJwQlA1UUJCbkdpMTg3VVFrOTk6aF85RG1EUDRSY0tNWE5wak9tVm9KQQ=="}
        )
        # print(query)
        return {"Total hits": res.get("hits", {}).get("total", {}).get("value",0),
            "Response": res.get("hits", {}).get("hits", [])}
    except Exception as e:
        logger.error(f"Failed to search logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to search logs: {str(e)}")