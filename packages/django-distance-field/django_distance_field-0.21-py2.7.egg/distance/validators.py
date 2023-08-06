from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils.six import string_types

def valid_unit_type(value):
    from .fields import DistanceField, D

    if not value: return

    if isinstance(value, string_types):
        try:
            r, f = DistanceField.parse_string(value)
        except Exception:
            raise ValidationError(_("Please enter a valid measurement."))
        if r == None or f == False:
            units = [g for g in list(D.ALIAS.values()) if '_' not in g]
            raise ValidationError(_("Please choose a valid measurement unit from"+\
                " %(units)s." % {'units': ", ".join(units)}))