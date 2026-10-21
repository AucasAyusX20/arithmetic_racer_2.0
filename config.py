# ==============================================================================
# FILE: config.py
# PURPOSE: Acts as the "database" for the game's difficulty and math balance.
#          Separating this from the logic makes the game easy to tune.
# ==============================================================================

# Each dictionary represents a difficulty tier.
# - "v0": Base speed of the lane scroll.
# - "D": Distance dial. Used to calculate time: Time = D / (v0 * multiplier)
# - "base_score": Points awarded before the streak multiplier is applied.
# - "ops": The math operations allowed in this tier (+, -, x)
TIERS = [
    {"v0": 10,  "D": 80,   "base_score": 10, "ops": "+"},
    {"v0": 19,  "D": 180,  "base_score": 20, "ops": "+"},
    {"v0": 35,  "D": 385,  "base_score": 35, "ops": "+-"},
    {"v0": 65,  "D": 812,  "base_score": 55, "ops": "+-x"},
    {"v0": 120, "D": 1680, "base_score": 80, "ops": "x"}
]

def get_tier_index(question_num):
    """
    Determines which tier the player is in based on how many questions they've answered.
    This ensures the difficulty scales steadily as the game progresses.
    """
    if question_num <= 5: return 0
    elif question_num <= 9: return 1
    elif question_num <= 13: return 2
    elif question_num <= 19: return 3
    return 4

def get_multiplier(question_num):
    """
    Calculates the score multiplier based on the current streak.
    It increases by 0.5 for every question answered, but caps at 5.0.
    """
    return min(5.0, 1.0 + (question_num - 1) * 0.5)