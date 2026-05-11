from fastapi import FastAPI
from fastapi import Depends
from app.routes.retention import router as retention_router

from sqlalchemy.orm import Session

from app.database import engine
from app.database import get_db
from app.database import Base
from app.schemas import TestSubmissionRequest

from app.retention_service import (
    process_test_submission
)


app = FastAPI()
app.include_router(retention_router)

Base.metadata.create_all(bind=engine)


@app.get("/")
def home():

    return {
        "message": "Retention Engine API Running"
    }


@app.post("/submit-test")
def submit_test(

    payload: TestSubmissionRequest,

    db: Session = Depends(get_db)
):

    result = process_test_submission(
        db,
        payload.dict()
    )

    return {
        "status": "success",
        "data": result
    }