from pydantic import BaseModel


class TestSubmissionRequest(BaseModel):

    user_id: int

    subject: str

    chapter_name: str

    question_type: str

    difficulty: str

    obtained_marks: float

    total_marks: float