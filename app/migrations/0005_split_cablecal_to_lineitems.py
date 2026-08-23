# pyright: reportAttributeAccessIssue=false, reportOptionalMemberAccess=false
from decimal import Decimal

from django.db import migrations


def _rows(field):
    """Split a newline-joined legacy text field into a list of values."""
    if not field:
        return []
    return field.split("\n")


def _value(lst, index, cast, default=None):
    """Safely get ``lst[index]`` coerced to ``cast``, or ``default``."""
    if index >= len(lst):
        return default
    raw = lst[index]
    if raw in ("", None):
        return default
    try:
        return cast(raw)
    except (ValueError, TypeError):
        return default


def split(apps, schema_editor):
    """Split each legacy CableCal's newline-joined fields into CableLineItem rows."""
    CableCal = apps.get_model("app", "CableCal")
    CableLineItem = apps.get_model("app", "CableLineItem")
    ReelsList = apps.get_model("app", "ReelsList")

    for calc in CableCal.objects.all():
        if calc.line_items.exists():
            continue  # already migrated

        cods = _rows(calc.cod)
        names = _rows(calc.name)
        order_lens = _rows(calc.order_len)
        masses = _rows(calc.mass)
        diameters = _rows(calc.diameter)
        con_nums = _rows(calc.con_num)
        max_lens = _rows(calc.max_len)
        reel_names = _rows(calc.reel_name)
        reel_nums = _rows(calc.reel_num)
        reel_lens = _rows(calc.reel_len)
        netto_1 = _rows(calc.netto_1)
        brutto_1 = _rows(calc.brutto_1)
        netto_all = _rows(calc.netto_all)
        brutto_all = _rows(calc.brutto_all)
        bending = _rows(calc.bending_radius)

        count = max(len(cods), len(names), len(order_lens), 1)
        for i in range(count):
            rname = _value(reel_names, i, str, "")
            reel = ReelsList.objects.filter(name=rname).first() if rname else None
            CableLineItem.objects.create(
                cable_cal=calc,
                position=i,
                cod=_value(cods, i, str, ""),
                name=_value(names, i, str, ""),
                con_num=_value(con_nums, i, int, 1),
                order_len=_value(order_lens, i, Decimal, Decimal("0")),
                max_len=_value(max_lens, i, Decimal, Decimal("0")),
                mass=_value(masses, i, Decimal, Decimal("0")),
                diameter=_value(diameters, i, Decimal, Decimal("0")),
                reel=reel,
                reel_len=_value(reel_lens, i, Decimal, Decimal("0")),
                reel_num=_value(reel_nums, i, int, 0),
                netto_1=_value(netto_1, i, Decimal, Decimal("0")),
                brutto_1=_value(brutto_1, i, Decimal, Decimal("0")),
                netto_all=_value(netto_all, i, Decimal, Decimal("0")),
                brutto_all=_value(brutto_all, i, Decimal, Decimal("0")),
                bending_radius=_value(bending, i, Decimal, Decimal("0")),
                warning="",
            )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0004_calcsettings_lineitem"),
    ]
    operations = [
        migrations.RunPython(split, noop),
    ]