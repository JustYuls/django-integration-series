"""Part 12: verify what an AI assistant said about the bug report.

Run from the project folder (after migrate):   python -m final_review.review
"""
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "campus_hub.settings")
django.setup()

from final_review import debug  # noqa: E402


def main():
    f = debug.evaluate()
    print("Bug report: 'Lab C is shown as busy 10:00-12:00, but it has no booking then.'")
    print(f"  buggy query, 10:00-12:00 -> {', '.join(f['buggy_10_to_12'])}")
    print(f"  fixed query, 10:00-12:00 -> {', '.join(f['fixed_10_to_12'])}")
    reproduced = "Lab C" not in f["buggy_10_to_12"] and "Lab C" in f["fixed_10_to_12"]
    two_subqueries = f["buggy_sql"].count("EXISTS(") == 2 and f["fixed_sql"].count("EXISTS(") == 1
    print(f"FINDING 1  the bug is reproduced: Lab C is wrongly excluded      {'confirmed' if reproduced else 'NOT confirmed'}")
    print(f"FINDING 2  the SQL has two separate EXISTS, the fix has one       {'confirmed' if two_subqueries else 'NOT confirmed'}")
    print(f"FINDING 3  the fix (one EXISTS) is one query, and correct          {'confirmed' if f['fixed_query_count'] == 1 and reproduced else 'NOT confirmed'}")
    boundary_ok = f["buggy_back_to_back"] == ["Open Studio", "Room A"]
    print(f"CLAIM 4    the boundary uses <= so back-to-back bookings clash     {'FALSE' if boundary_ok else 'TRUE'}  (Room A is free at 11:00)")
    print(f"CLAIM 5    select_related() fixes it                                {'FALSE' if f['with_select_related'] == f['buggy_10_to_12'] else 'TRUE'}  (same wrong answer)")
    print(f"CLAIM 6    one EXISTS subquery fixes it                             {'TRUE' if reproduced else 'FALSE'}")


if __name__ == "__main__":
    main()
