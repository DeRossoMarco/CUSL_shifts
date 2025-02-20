import random
import time
import csv

def load_availability(config, file_name):
    availability = {}
    with open(file_name, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            person = row['Nome']
            person_availability = [
                shift for shift in config.weekly_shifts
                if row[shift].lower() == 'si'
            ]
            availability[person] = person_availability
    return availability

def generate_shifts(config, availability):
    shifts = []
    for day in config.weekly_shifts:
        random.seed(time.time_ns())
        available_people = [
            p for p in availability if day in availability[p]
        ]
        if len(available_people) >= config.MIN_PEOPLE_PER_SHIFT:
            chosen = random.sample(
                available_people,
                random.randint(
                    config.MIN_PEOPLE_PER_SHIFT,
                    min(config.MAX_PEOPLE_PER_SHIFT, len(available_people))
                )
            )
        else:
            return []
        for p in chosen:
            availability.pop(p)
        shifts.append((day, chosen))
    if len(availability) != 0:
        return []
    return shifts