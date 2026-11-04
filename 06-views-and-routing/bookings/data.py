"""Sample rooms. Part 7 replaces this list with a database model."""
ROOMS = [
    {"id": 1, "name": "Room 101", "capacity": 40},
    {"id": 2, "name": "Lab A", "capacity": 30},
    {"id": 3, "name": "Gym", "capacity": 80},
]


def find_room(room_id):
    return next((room for room in ROOMS if room["id"] == room_id), None)
