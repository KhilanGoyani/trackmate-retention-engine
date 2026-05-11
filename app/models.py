from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Boolean,
    DateTime
)

from datetime import datetime

from app.database import Base


class RetentionState(Base):

    __tablename__ = "retention_states"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer)

    subject = Column(String)

    chapter_name = Column(String)

    question_type = Column(String)

    difficulty = Column(String)

    stability = Column(Float, default=5)

    revision_count = Column(Integer, default=0)

    last_score = Column(Float)

    retention = Column(Float)

    weak_topic = Column(Boolean)

    last_activity_at = Column(DateTime, default=datetime.utcnow)
    
    momentum = Column(Float, default=0)

    priority_score = Column(Float, default=0)

    decay_rate = Column(Float, default=1)

    consistency_score = Column(Float, default=0)

    forgetting_loss = Column(Float, default=0)

    learning_gain = Column(Float, default=0)

    days_passed = Column(Integer, default=0)