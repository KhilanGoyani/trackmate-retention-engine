import math


# ======================================
# CONFIGURATION
# ======================================

RETENTION_THRESHOLD = 40
INITIAL_STABILITY = 5


# ======================================
# SIMULATED DATABASE
# ======================================

student_memory_db = {}


# ======================================
# SCORE PERCENTAGE
# ======================================

def calculate_score_percentage(obtained_marks, total_marks):

    if total_marks == 0:
        return 0

    return round((obtained_marks / total_marks) * 100, 2)


# ======================================
# PERFORMANCE GAIN
# ======================================

def get_performance_gain(score_percentage):

    if score_percentage >= 90:
        return 3

    elif score_percentage >= 70:
        return 2

    elif score_percentage >= 40:
        return 1

    return 0


# ======================================
# DIFFICULTY MODIFIER
# ======================================

def get_difficulty_modifier(difficulty):

    difficulty = difficulty.lower()

    mapping = {
        "easy": 1,
        "medium": 0,
        "hard": -1
    }

    return mapping.get(difficulty, 0)


# ======================================
# UPDATE STABILITY
# ======================================

def update_stability(
    previous_stability,
    score_percentage,
    difficulty,
    revision_count
):

    performance_gain = get_performance_gain(score_percentage)

    difficulty_modifier = get_difficulty_modifier(difficulty)

    revision_bonus = math.log(revision_count + 1)

    new_stability = (
        previous_stability
        + performance_gain
        + difficulty_modifier
        + revision_bonus
    )

    return round(new_stability, 2)


# ======================================
# RETENTION FORMULA
# ======================================

def calculate_retention(
    initial_retention,
    stability,
    days_passed
):

    retention = (
        initial_retention
        * math.exp(-days_passed / stability)
    )

    return round(retention, 2)


# ======================================
# WEAK TOPIC DETECTION
# ======================================

def is_weak_topic(retention):

    return retention < RETENTION_THRESHOLD


# ======================================
# PROCESS TEST
# ======================================

def process_test(test_data):

    chapter = test_data["chapter"]

    obtained_marks = test_data["obtained_marks"]

    total_marks = test_data["total_marks"]

    difficulty = test_data["difficulty"]

    days_passed = test_data["days_passed"]


    # ==================================
    # LOAD PREVIOUS MEMORY STATE
    # ==================================

    if chapter in student_memory_db:

        previous_state = student_memory_db[chapter]

        previous_stability = previous_state["stability"]

        revision_count = previous_state["revision_count"]

    else:

        previous_stability = INITIAL_STABILITY

        revision_count = 0


    # ==================================
    # SCORE %
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
    # RETENTION CALCULATION
    # ==================================

    retention = calculate_retention(
        score_percentage,
        stability,
        days_passed
    )


    # ==================================
    # WEAK TOPIC DETECTION
    # ==================================

    weak_topic = is_weak_topic(retention)


    # ==================================
    # SAVE UPDATED MEMORY STATE
    # ==================================

    student_memory_db[chapter] = {

        "stability": stability,

        "revision_count": revision_count
    }


    # ==================================
    # FINAL RESULT
    # ==================================

    result = {

        "chapter": chapter,

        "score_percentage": score_percentage,

        "stability": stability,

        "revision_count": revision_count,

        "retention": retention,

        "weak_topic": weak_topic
    }

    return result


# ======================================
# TEST CASES
# ======================================

tests = [

    {
        "chapter": "Number Systems",
        "obtained_marks": 1,
        "total_marks": 20,
        "difficulty": "Hard",
        "days_passed": 2
    },

    {
        "chapter": "Number Systems",
        "obtained_marks": 12,
        "total_marks": 20,
        "difficulty": "Easy",
        "days_passed": 5
    },

    {
        "chapter": "Number Systems",
        "obtained_marks": 20,
        "total_marks": 20,
        "difficulty": "Medium",
        "days_passed": 10
    }
]


# ======================================
# RUN ENGINE
# ======================================

print("\n========= RETENTION ENGINE =========\n")

for test in tests:

    result = process_test(test)

    print("----------------------------------")

    for key, value in result.items():

        print(f"{key}: {value}")