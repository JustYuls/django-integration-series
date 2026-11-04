"""Part 10: verify what an AI said when reviewing the design of the app.

Run from the project folder:   python -m design_review.review
"""
from design_review import check_imports as ci

FLAWED_GRAPH = {"rooms": {"bookings"}, "bookings": {"rooms", "holiday_api"}, "holiday_api": set()}  # what a bad design would look like


def evaluate():
    graph = ci.build_graph()
    return {
        "graph": graph,
        "cycle": ci.find_cycle(graph),
        "violations": ci.violations(graph),
        "rooms_imports_bookings": "bookings" in graph["rooms"],
        "holiday_api_is_independent": not graph["holiday_api"],
        "views_use_services": ci.views_use_services(),
        "views_call_mail_directly": ci.views_call_mail_directly(),
        "flawed_cycle": ci.find_cycle(FLAWED_GRAPH),
        "flawed_violations": ci.violations(FLAWED_GRAPH),
    }


def main():
    f = evaluate()
    print("App dependency graph (built from the real imports):")
    for app, deps in f["graph"].items():
        print(f"  {app:<12} -> {', '.join(sorted(deps)) or '(nothing)'}")
    ok = lambda b: "confirmed" if b else "NOT confirmed"  # noqa: E731
    print(f"FINDING 1  {'one-way dependency: bookings -> rooms':<52} {ok(not f['violations'] and not f['rooms_imports_bookings'])}")
    print(f"FINDING 2  {'the workflow lives in services.py, not in views':<52} {ok(f['views_use_services'] and not f['views_call_mail_directly'])}")
    print(f"FINDING 3  {'holiday_api is self-contained':<52} {ok(f['holiday_api_is_independent'])}")
    print(f"CLAIM 4    {'there is a circular import between rooms and bookings':<52} {'FALSE' if f['cycle'] is None else 'TRUE'}  (no cycle found)")
    print(f"CLAIM 5    {'the rooms app imports the bookings app':<52} {'FALSE' if not f['rooms_imports_bookings'] else 'TRUE'}")
    print(f"CLAIM 6    {'a cycle would be detected by our checker':<52} {'TRUE' if f['flawed_cycle'] else 'FALSE'}  ({' -> '.join(f['flawed_cycle'] or [])})")


if __name__ == "__main__":
    import os

    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "campus_hub.settings")
    main()
