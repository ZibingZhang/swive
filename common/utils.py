from __future__ import annotations

from decimal import Decimal

from django.urls import reverse
from django.utils.html import format_html

from common.constants import SEED_REGEX


# https://stackoverflow.com/a/53092940
def linkify_fk(field_name: str):
    """
    Converts a foreign key value into clickable links.

    If field_name is 'parent', link text will be str(obj.parent)
    Link will be admin url for the admin url for obj.parent.id:change
    """

    def _linkify_fk(obj):
        linked_obj = getattr(obj, field_name)
        if linked_obj is None:
            return "-"
        app_label = linked_obj._meta.app_label
        model_name = linked_obj._meta.model_name
        view_name = f"admin:{app_label}_{model_name}_change"
        link_url = reverse(view_name, args=[linked_obj.pk])
        return format_html('<a href="{}">{}</a>', link_url, linked_obj)

    _linkify_fk.short_description = field_name  # Sets column name
    return _linkify_fk


def is_seed(seed: str) -> bool:
    return SEED_REGEX.match(seed) and seed != "."


def seed_to_decimal(seed: str) -> Decimal:
    if ":" not in seed:
        return Decimal("0" + seed)
    minutes, seconds = seed.split(":")
    seconds, milliseconds = seconds.split(".")
    seconds = str(60 * int(minutes) + int(seconds))
    return Decimal(f"{seconds}.{milliseconds}")
