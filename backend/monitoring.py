def check_if_stuck(lmi_history: list) -> bool:
    """
    Determines if learning has stagnated.
    """

    # If LMI hasn't increased significantly across attempts
    if len(lmi_history) < 2:
        return False

    return abs(lmi_history[-1] - lmi_history[-2]) < 5
