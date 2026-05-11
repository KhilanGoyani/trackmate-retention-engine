from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database import get_db

from app.retention_service import (
    process_exam_submission,
    process_real_exam_result,
    process_test_history
)

router = APIRouter()


@router.post("/process-exam")
def process_exam(

    payload: dict,

    db: Session = Depends(get_db)
):

    result = process_exam_submission(
        db,
        payload
    )

    return {
        "status": "success",
        "data": result
    }


@router.post("/process-real-exam")
def process_real_exam(

    payload: dict,

    db: Session = Depends(get_db)
):

    result = process_real_exam_result(
        db,
        payload
    )

    return {
        "status": "success",
        "data": result
    }


@router.post("/process-test-history")
def process_history(

    payload: dict,

    db: Session = Depends(get_db)
):

    result = process_test_history(
        db,
        payload
    )

    return {
        "status": "success",
        "data": result
    }