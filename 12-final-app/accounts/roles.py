"""Roles are groups of permissions. People get a role, not a list of individual permissions."""
from django.apps import apps
from django.contrib.auth.management import create_permissions
from django.contrib.auth.models import Group, Permission

STUDENT = "Student"
STAFF = "Staff"

STUDENT_PERMISSIONS = [("bookings", "view_booking"), ("bookings", "add_booking"), ("bookings", "change_booking"), ("bookings", "delete_booking")]
STAFF_PERMISSIONS = STUDENT_PERMISSIONS + [("bookings", "manage_all_bookings"), ("rooms", "add_room"), ("rooms", "change_room"), ("rooms", "delete_room")]

ROLES = {STUDENT: STUDENT_PERMISSIONS, STAFF: STAFF_PERMISSIONS}


def create_roles(sender=None, **kwargs):
    if sender is None or sender.label != "bookings":  # post_migrate is sent once per app: act after bookings
        return
    for app_label in ("rooms", "bookings"):
        create_permissions(apps.get_app_config(app_label), verbosity=0)  # make sure the permissions exist first
    for name, wanted in ROLES.items():
        group, _ = Group.objects.get_or_create(name=name)
        group.permissions.set([Permission.objects.get(content_type__app_label=app, codename=code) for app, code in wanted])
