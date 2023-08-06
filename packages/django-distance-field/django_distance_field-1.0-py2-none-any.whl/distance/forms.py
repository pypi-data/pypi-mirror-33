from django.forms import fields
from django.forms.widgets import TextInput
from django.forms.utils import flatatt
from django.utils.html import conditional_escape, format_html

from . import validators

class DistanceField(fields.CharField):
    default_validators = [validators.valid_unit_type]
    
    def __init__(self, *args, **kwargs):
        super(DistanceField, self).__init__(*args, **kwargs)
