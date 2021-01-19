from datetime import datetime


# костыль, перенести в нормальное место после TMBT-70

def matches_the_time(after: datetime, activity_start: datetime) -> bool:
    return after <= activity_start
