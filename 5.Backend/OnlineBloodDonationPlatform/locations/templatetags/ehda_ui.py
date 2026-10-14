from django import template


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
