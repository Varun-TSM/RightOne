import datetime

def split_into_half_hour_slots(start_time, end_time):
    slots = []
    current = datetime.datetime.combine(datetime.date.today(), start_time)
    end = datetime.datetime.combine(datetime.date.today(), end_time)

    while current + datetime.timedelta(minutes=30) <= end:
        slots.append(current.time())
        current += datetime.timedelta(minutes=30)

    return slots