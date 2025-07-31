import csv

from models.venue import Venue

def is_duplicate_venue(venue_name: str, seen_names: set) -> bool:
    return venue_name in seen_names

def is_complete_venue(venue: Venue, required_keys: list) -> bool:
    return all(key in venue for key in required_keys)

def save_venues_to_csv(venues: list, filename: str):
    if not venues:
        print("No venues to save.")
        return

    with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
        fieldnames = venues[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for venue in venues:
            writer.writerow(venue)

    print(f"Saved venues to {filename}.")