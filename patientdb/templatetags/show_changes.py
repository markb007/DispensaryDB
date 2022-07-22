""" from django import template
from dispensary.patientdb.models import HerbalMedicine

register = template.Library()

@register.inclusion_tag('patientdb/changes.html')
def show_changes():
    changes = HerbalMedicine.objects.all()
    return {'changes': changes} """