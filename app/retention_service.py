import math

from datetime import datetime

from sqlalchemy.orm import Session

from app.models import RetentionState


# ======================================
# CONFIGURATION
# ======================================

RETENTION_CONFIG = {

    # Initial values
    "initial_retention": 50,
    "initial_stability": 5,

    # Weak topic thresholds
    "difficulty_thresholds": {
        "easy": 55,
        "medium": 45,
        "hard": 35
    },

    # Difficulty impact
    "difficulty_modifiers": {
        "easy": 1,
        "medium": 0,
        "hard": -1
    },

    # Performance gain
    "performance_gains": {
        90: 3,
        70: 2,
        40: 1
    },

    # Stability limit
    "max_stability": 25
}


# ======================================
# SCORE PERCENTAGE
# ======================================

def calculate_score_percentage(
    obtained_marks,
    total_marks
):

    if total_marks == 0:
        return 0

    return round(
        (obtained_marks / total_marks) * 100,
        2
    )


# ======================================
# PERFORMANCE GAIN
# ======================================

def get_performance_gain(score_percentage):

    gains = RETENTION_CONFIG[
        "performance_gains"
    ]

    if score_percentage >= 90:
        return gains[90]

    elif score_percentage >= 70:
        return gains[70]

    elif score_percentage >= 40:
        return gains[40]

    return 0


# ======================================
# DIFFICULTY MODIFIER
# ======================================

def get_difficulty_modifier(difficulty):

    return RETENTION_CONFIG[
        "difficulty_modifiers"
    ].get(
        difficulty.lower(),
        0
    )


# ======================================
# UPDATE STABILITY
# ======================================

def update_stability(
    previous_stability,
    score_percentage,
    difficulty,
    revision_count
):

    performance_gain = get_performance_gain(
        score_percentage
    )

    difficulty_modifier = get_difficulty_modifier(
        difficulty
    )

    revision_bonus = math.log(
        revision_count + 1
    )

    new_stability = (
        previous_stability
        + performance_gain
        + difficulty_modifier
        + revision_bonus
    )

    return round(
        min(
            new_stability,
            RETENTION_CONFIG[
                "max_stability"
            ]
        ),
        2
    )


# ======================================
# RETENTION FORMULA
# ======================================

def calculate_retention(
    memory_strength,
    stability,
    days_passed
):

    retention = (
        memory_strength
        * math.exp(
            -days_passed / stability
        )
    )

    return round(retention, 2)


# ======================================
# WEAK TOPIC DETECTION
# ======================================

def is_weak_topic(
    retention,
    difficulty
):

    threshold = RETENTION_CONFIG[
        "difficulty_thresholds"
    ].get(
        difficulty.lower(),
        45
    )

    return retention < threshold


# ======================================
# MOMENTUM
# ======================================

def calculate_momentum(
    previous_score,
    current_score
):

    return round(
        current_score - previous_score,
        2
    )


# ======================================
# PRIORITY SCORE
# ======================================

def calculate_priority_score(
    retention,
    stability,
    revision_count
):

    priority_score = (
        (100 - retention)
        + (10 - stability)
        - (revision_count * 0.5)
    )

    return round(priority_score, 2)


# ======================================
# MAIN ENGINE
# ======================================

def process_test_submission(
    db: Session,
    payload: dict
):

    user_id = payload["user_id"]

    subject = payload["subject"]

    chapter_name = payload["chapter_name"]

    question_type = payload["question_type"]

    difficulty = payload["difficulty"]

    obtained_marks = payload["obtained_marks"]

    total_marks = payload["total_marks"]


    # ==================================
    # FETCH EXISTING MEMORY STATE
    # ==================================

    existing_state = db.query(
        RetentionState
    ).filter(

        RetentionState.user_id == user_id,

        RetentionState.chapter_name == chapter_name,

        RetentionState.question_type == question_type

    ).first()


    # ==================================
    # NEW OR EXISTING TOPIC
    # ==================================

    if existing_state is None:

        previous_stability = RETENTION_CONFIG[
            "initial_stability"
        ]

        revision_count = 0

        previous_retention = RETENTION_CONFIG[
            "initial_retention"
        ]

        previous_score = 0

        days_passed = 0

    else:

        previous_stability = existing_state.stability

        revision_count = existing_state.revision_count

        previous_retention = existing_state.retention

        previous_score = existing_state.last_score

        last_activity = existing_state.last_activity_at

        time_difference = (
            datetime.utcnow()
            - last_activity
        )

        days_passed = (
            time_difference.total_seconds()
            / 86400
        )


    # ==================================
    # CURRENT SCORE
    # ==================================

    score_percentage = calculate_score_percentage(
        obtained_marks,
        total_marks
    )


    # ==================================
    # UPDATE REVISION COUNT
    # ==================================

    revision_count += 1


    # ==================================
    # UPDATE STABILITY
    # ==================================

    stability = update_stability(
        previous_stability,
        score_percentage,
        difficulty,
        revision_count
    )


    # ==================================
    # MEMORY BLENDING
    # ==================================

    memory_strength = (
        previous_retention * 0.7
    )

    performance_strength = (
        score_percentage * 0.3
    )

    current_memory = (
        memory_strength
        + performance_strength
    )


    # ==================================
    # RETENTION CALCULATION
    # ==================================

    retention = calculate_retention(
        current_memory,
        stability,
        days_passed
    )


    # ==================================
    # WEAK TOPIC
    # ==================================

    weak_topic = is_weak_topic(
        retention,
        difficulty
    )


    # ==================================
    # MOMENTUM
    # ==================================

    momentum = calculate_momentum(
        previous_score,
        score_percentage
    )


    # ==================================
    # PRIORITY SCORE
    # ==================================

    priority_score = calculate_priority_score(
        retention,
        stability,
        revision_count
    )


    # ==================================
    # SAVE DATABASE
    # ==================================

    if existing_state is None:

        new_state = RetentionState(

            user_id=user_id,

            subject=subject,

            chapter_name=chapter_name,

            question_type=question_type,

            difficulty=difficulty,

            stability=stability,

            revision_count=revision_count,

            last_score=score_percentage,

            retention=retention,

            weak_topic=weak_topic,

            momentum=momentum,

            priority_score=priority_score,

            last_activity_at=datetime.utcnow()
        )

        db.add(new_state)

    else:

        existing_state.stability = stability

        existing_state.revision_count = revision_count

        existing_state.last_score = score_percentage

        existing_state.retention = retention

        existing_state.weak_topic = weak_topic

        existing_state.momentum = momentum

        existing_state.priority_score = priority_score

        existing_state.last_activity_at = datetime.utcnow()


    db.commit()


    # ==================================
    # RESPONSE
    # ==================================

    return {

        "user_id": user_id,

        "subject": subject,

        "chapter_name": chapter_name,

        "question_type": question_type,

        "score_percentage": score_percentage,

        "stability": stability,

        "revision_count": revision_count,

        "retention": retention,

        "weak_topic": weak_topic,

        "days_passed": round(days_passed, 1),

        "momentum": momentum,

        "priority_score": priority_score
    }
    
    
def process_exam_submission(
    db: Session,
    payload: dict
):

    user_id = payload["user_id"]

    subject = payload["subject"]

    difficulty = payload["difficulty"]

    obtained_marks = payload["obtained_marks"]

    total_marks = payload["total_marks"]

    chapter_titles = payload["chapter_titles"]


    all_results = []


    # ==================================
    # PROCESS EACH CHAPTER
    # ==================================

    combined_chapters = ", ".join(
        chapter_titles
    )


    payload_data = {

        "user_id": user_id,

        "subject": subject,

        "chapter_name": combined_chapters,

        "question_type": "mixed",

        "difficulty": difficulty,

        "obtained_marks": obtained_marks,

        "total_marks": total_marks
    }


    result = process_test_submission(
        db,
        payload_data
    )


    return result

def process_real_exam_result(
    db: Session,
    exam_result: dict
):

    test_data = exam_result["data"]


    obtained_marks = test_data[
        "obtained_marks"
    ]

    total_marks = test_data[
        "total_marks"
    ]


    # ==================================
    # DEFAULT DIFFICULTY
    # ==================================

    difficulty = test_data.get(
        "difficulty",
        "medium"
    )


    # ==================================
    # CHAPTER EXTRACTION
    # ==================================

    chapter_titles = test_data.get(
        "chapter_titles",
        []
    )


    # ==================================
    # BUILD PAYLOAD
    # ==================================

    payload = {

        "user_id": 246,

        "subject": "mathematics",

        "difficulty": difficulty,

        "obtained_marks": obtained_marks,

        "total_marks": total_marks,

        "chapter_titles": chapter_titles
    }


    return process_exam_submission(
        db,
        payload
    )
    

def process_test_history(

    db: Session,

    payload: dict
):

    test_list = payload["data"]["list"]

    all_results = []


    # ==================================
    # PROCESS EACH TEST
    # ==================================

    for test in test_list:

        obtained_marks = test[
            "obtained_marks"
        ]

        total_marks = test[
            "total_marks"
        ]

        difficulty = test[
            "difficulty"
        ]

        chapter_titles = test[
            "chapter_titles"
        ]


        combined_chapters = ", ".join(
            chapter_titles
        )


        test_payload = {

            "user_id": 246,

            "subject": "mathematics",

            "chapter_name": combined_chapters,

            "question_type": "mixed",

            "difficulty": difficulty,

            "obtained_marks": obtained_marks,

            "total_marks": total_marks
        }


        result = process_test_submission(
            db,
            test_payload
        )

        all_results.append(result)


    return all_results