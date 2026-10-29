from django import template

from locations.utils import public_name as _public_name


register = template.Library()


@register.filter
def blood_symbol(blood_type):
    """'O-' -> 'O−' using a real minus sign for display."""
    return (blood_type or "").replace("-", "−")


@register.filter
def blood_name(blood_type):
    """'O-' -> 'O negative', for screen readers."""
    if not blood_type:
        return ""

    group = blood_type.rstrip("+-")
    sign = "positive" if blood_type.endswith("+") else "negative"

    return f"{group} {sign}"


@register.filter
def public_name(user):
    """First name and last initial only ("Ahmad S."), never the full name."""
    return _public_name(user)
