"""Part 5: verify what an AI review said about the flawed project.

Run from the project folder:   python -m ai_review.review
"""
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "campus_hub.settings")
django.setup()

from django.apps import apps  # noqa: E402
from django.core.checks import run_checks  # noqa: E402
from django.template import Context, Template, TemplateDoesNotExist, TemplateSyntaxError  # noqa: E402
from django.template.loader import get_template  # noqa: E402
from django.test import override_settings  # noqa: E402

from ai_review.flawed import BAD_TEMPLATE, flawed_settings  # noqa: E402


def raises(exception, call):
    try:
        call()
    except exception:
        return True
    return False


def render_home():
    get_template("home.html")


def render_bad_template():
    Template(BAD_TEMPLATE).render(Context())


def evaluate():
    """Return the facts behind each AI finding and claim."""
    # DEBUG and ALLOWED_HOSTS are set explicitly: the test runner changes both,
    # but the project defaults are what we review.
    with override_settings(DEBUG=True, ALLOWED_HOSTS=[], **flawed_settings()):
        check_ids = [m.id for m in run_checks()]
        deploy_ids = [m.id for m in run_checks(include_deployment_checks=True)]
        facts = {
            "app_not_registered": not apps.is_installed("bookings"),
            "template_folder_typo": raises(TemplateDoesNotExist, render_home),
            "static_folder_missing": "staticfiles.W004" in check_ids,
            "static_without_load": raises(TemplateSyntaxError, render_bad_template),
            "debug_and_hosts": "security.W018" in deploy_ids and "security.W020" in deploy_ids,
            "check_ids": check_ids,
            "deploy_only": "security.W018" not in check_ids and "security.W020" not in check_ids,
        }
    with override_settings(DEBUG=False, **flawed_settings()):
        facts["debug_false_fixes_template"] = not raises(TemplateDoesNotExist, render_home)
    return facts


def main():
    f = evaluate()
    found_by_check = {1: False, 2: False, 3: "staticfiles.W004" in f["check_ids"], 4: False, 5: False}
    rows = [
        (1, "App 'bookings' is not registered", f["app_not_registered"], "missed"),
        (2, "Template folder typo ('template')", f["template_folder_typo"], "missed"),
        (3, "STATICFILES_DIRS folder is missing", f["static_folder_missing"], "FOUND (staticfiles.W004)"),
        (4, "{% static %} without {% load static %}", f["static_without_load"], "missed"),
        (5, "DEBUG on, ALLOWED_HOSTS empty", f["debug_and_hosts"], "missed (only check --deploy)"),
    ]
    for n, text, confirmed, by_check in rows:
        print(f"ISSUE {n}  {text:<40} {'confirmed' if confirmed else 'NOT confirmed':<14} manage.py check: {by_check}")
    verdict6 = "TRUE" if all(found_by_check.values()) else "FALSE"
    verdict7 = "TRUE" if f["debug_false_fixes_template"] else "FALSE"
    print(f"CLAIM 6  {'check flags all five':<40} {verdict6}  (found {sum(found_by_check.values())} of 5)")
    print(f"CLAIM 7  {'DEBUG = False fixes the template':<40} {verdict7}  (TemplateDoesNotExist remains)")


if __name__ == "__main__":
    main()
