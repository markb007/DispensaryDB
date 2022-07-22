from import_export import resources, fields
from import_export.widgets import ManyToManyWidget
from .models import HerbalFormula, FormulaHerbItem

class HerbalFormulaResource(resources.ModelResource):
    # quantities = fields.Field(widget=ManyToManyWidget(FormulaHerbItem, field='quantity'))
    class Meta:
        model = FormulaHerbItem
        # fields = ['formula_id', 'formula_code', 'formula_type', 'formula_ingredients', 'quantities', ]