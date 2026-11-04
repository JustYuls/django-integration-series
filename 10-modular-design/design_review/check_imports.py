"""Part 10: build the import graph between our apps, and check the design rules against it."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APPS = ["rooms", "bookings", "holiday_api"]

# The design rule: who may import whom. Dependencies point one way, and nothing is circular.
ALLOWED = {"rooms": set(), "holiday_api": set(), "bookings": {"rooms", "holiday_api"}}


def imports_of(path):
    """The top-level module names imported by one Python file."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.add(node.module.split(".")[0])
    return names


def real_files(app):
    for path in (ROOT / app).rglob("*.py"):
        if "migrations" in path.parts or path.name == "tests.py" or path.name.startswith("test_"):
            continue  # tests may import any app, and migrations only name apps as strings
        yield path


def build_graph():
    graph = {}
    for app in APPS:
        used = set()
        for path in real_files(app):
            used |= imports_of(path) & set(APPS)
        graph[app] = used - {app}
    return graph


def find_cycle(graph):
    """Return a list like ['rooms', 'bookings', 'rooms'] if there is a circular dependency, else None."""
    def visit(node, path):
        if node in path:
            return path[path.index(node):] + [node]
        for neighbour in sorted(graph.get(node, ())):
            found = visit(neighbour, path + [node])
            if found:
                return found
        return None

    for start in sorted(graph):
        found = visit(start, [])
        if found:
            return found
    return None


def violations(graph, allowed=ALLOWED):
    return sorted((app, used) for app, deps in graph.items() for used in deps if used not in allowed.get(app, set()))


def views_call_mail_directly():
    """True if bookings/views.py imports mail code itself instead of going through the service."""
    names = imports_of(ROOT / "bookings" / "views.py")
    source = (ROOT / "bookings" / "views.py").read_text(encoding="utf-8")
    return "send_mail" in source or "notifications" in source or "django" in names and "django.core.mail" in source


def views_use_services():
    return "services" in (ROOT / "bookings" / "views.py").read_text(encoding="utf-8")
