from django.contrib import admin

# Register your models here.

from .models import Patient, PatientDetail, PatientConsult, HerbalMedicine, HerbIndication, HerbAction, Product
from .models import HerbalFormula, Supplier, Brand, DispensedItem, FormulaHerbItem
from .models import UserProfile, Settings, HealthFund, ProductStrength, FormulaBottleSize, FormulaSetting

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from import_export.admin import ImportExportModelAdmin
from import_export import resources


# define actual key field for django-import-export as for this model it's not 'id'
class HerbalMedicineResource(resources.ModelResource):
    
    class Meta:
         model = HerbalMedicine
         import_id_fields = ['herb_id']

# define actual key field for django-import-export as for this model it's not 'id'
class ProductResource(resources.ModelResource):
    
    class Meta:
         model = Product
         import_id_fields = ['product_id']

# Define an inline admin descriptor for UserProfile model
# which acts a bit like a singleton
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'userprofile'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

"""
Inlines required in order to relate patient detail and patient consult tables to patient
on the change page
"""
class PatientDetailInLine(admin.StackedInline):
    model = PatientDetail
    readonly_fields=('created', 'modified',)

class PatientConsultInLine(admin.StackedInline):
    model = PatientConsult
    readonly_fields=('created', 'modified',)
    extra = 1

class PatientFormulaInLine(admin.TabularInline):
    model = HerbalFormula.patient_formulas.through
    extra = 1

class FormulaItemsInLine(admin.TabularInline):
    model = HerbalFormula.formula_ingredients.through
    extra= 1

class PatientInLine(admin.TabularInline):
    model = HerbalFormula.patient_formulas.through
    readonly_fields=('created', 'modified',)
    extra = 1

''' class ProductInLine(admin.TabularInline):
    ordering = ('product_name', )
    model = Product
    extra = 1 '''

class BrandInLine(admin.TabularInline):
    model = Brand.supplier_brand.through
    extra = 1


"""
Inline declaration for many to many relationship with Herbal Medicine class
Enables this relationship to display on same page as Herbal Medicine
"""
class ActionsInline(admin.TabularInline):
    model = HerbAction.herbmed_actions.through


class IndicationsInline(admin.TabularInline):
    model = HerbIndication.herbmed_indications.through


class PatientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'address_1', 'city', 'postcode', 'mobile', 'email', 'created', 'modified', )
    search_fields = ('first_name', 'last_name', 'mobile', 'email')
    list_filter = ('modified', )
    date_hierarchy = 'modified'
    ordering = ('-modified', )

    """
    display related models on the same change page
    """
    inlines = [
        PatientDetailInLine,
        PatientConsultInLine,
        PatientFormulaInLine,
    ]


class PatientConsultAdmin(admin.ModelAdmin):
    list_display = ('patient_consult', 'summary', 'created', )
    list_filter = ('created', )
    search_fields = ('patient_consult__first_name', 'patient_consult__last_name')
    date_hierarchy = 'created'
    ordering = ('-created', )


class PatientDetailAdmin(admin.ModelAdmin):
    list_display = ('patient', 'allergies', 'medication', 'surgery', 'occupation', 'modified', )
    list_filter = ('modified', )
    search_fields = ('patient__first_name', 'patient__last_name')
    date_hierarchy = 'modified'
    ordering = ('-modified', )


class HerbalMedicineAdmin(ImportExportModelAdmin):
    # indicate resource class as primary key is not called 'id'
    resource_class = HerbalMedicineResource
    list_display = ('herb_name', 'herb_botanical_name', 'created', 'modified')
    search_fields = ('herb_name', 'herb_botanical_name',)
    ordering = ('herb_name', )

    """
    This enables the herb actions and herb indications to be displayed inline on the Herbal Medicine page
    as well as related products for this herbal medicine
    Refer ActionsInline and IndicationsInline classes above
    """
    inlines = [
        ActionsInline,
        IndicationsInline,
        # ProductInLine,
    ]


class HerbIndicationAdmin(admin.ModelAdmin):
    list_display = ('herbindication_name', )
    search_fields = ('herbindication_name', )
    ordering = ('herbindication_name', )

    """
    allow parent table HerbalMedicines to be selectable on same display page
    """
    filter_horizontal = ('herbmed_indications', )


class HerbActionAdmin(ImportExportModelAdmin):
    list_display = ('herbaction_name', )
    search_fields = ('herbaction_name', )
    ordering = ('herbaction_name', )

    """
    allow parent table HerbalMedicines to be selectable on same display page
    """
    filter_horizontal = ('herbmed_actions', )


class HerbalFormulaAdmin(ImportExportModelAdmin):
    list_display = ('formula_code', 'created', )
    search_fields = ('formula_code', )

    inlines = [
        FormulaItemsInLine,
        PatientInLine,
    ]


class DispensedItemAdmin(admin.ModelAdmin):
    list_display = ('formula_code', 'dispensed_to', 'quantity', 'measure', 'directions', 'created', )
    search_fields = ('formula_code', 'dispensed_to', )
    list_filter = ('created', )
    date_hierarchy = 'created'
    ordering = ('-created', )

    """
    the correct way of referencing foreign key fields in related model
    using the syntax 'xxx__field' doesn't work for list_display but does for search_fields
    """

    def formula_code(self, obj):
        return obj.formula.formula_code

    def dispensed_to(self, obj):
        return obj.patient


class SupplierAdmin(ImportExportModelAdmin):
    list_display = ('supplier_name', 'address_1', 'city', 'state', 'postcode', 'created')
    inlines = [
        BrandInLine,
    ]


class BrandAdmin(ImportExportModelAdmin):
    """
    exclude the many to many with supplier so we can declare an inline instead
    """
    exclude = ('supplier_brand', )

    list_display = ('brand_name', 'brand_short', 'created', 'modified')
    ordering = ('brand_name', )

    inlines = [
        BrandInLine,
        # ProductInLine, 
    ]


class HealthFundAdmin(ImportExportModelAdmin):
    list_display = ('fund_name', 'provider_no', )
    ordering = ('fund_name', )


class ProductStrengthsAdmin(ImportExportModelAdmin):
    list_display = ('strength', )
    ordering = ('strength', )


class FormulaSettingAdmin(ImportExportModelAdmin):
    list_display = ('formula_bottle_size', 'formula_bottle_cost', 'formula_bottle_size_mu', 'formula_bottle_size_min_rrp', \
        'formula_dispensing_fee')
    ordering = ('formula_bottle_size', )


class FormulaBottleSizesAdmin(ImportExportModelAdmin):
    list_display = ('bottle_size', 'bottle_unit', 'bottle_notes', )
    ordering = ('bottle_size', )


class FormulaHerbItemAdmin(ImportExportModelAdmin):
    list_display = ('formula', 'quantity')
    ordering = ('id', )


class ProductAdmin(ImportExportModelAdmin):
    # indicate resource class as primary key is not called 'id'
    resource_class = ProductResource
    list_display = ('product_name', 'product_code', 'product_strength', 'product_qty', 'product_cost', 'product_brand')

    """
    search field for a foreign key is the foreign key name (product_brand) appended by double underscore
    to the field in the related model that we want to search on (brand_name)
    """
    search_fields = ('product_name', 'product_brand__brand_name')
    ordering = ('product_name', )

    """
    allow for search box rather than select box due to number of herbal medicines.
    Foreign key is passed.
    """
    raw_id_fields = ('herbmed_product', )

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(HealthFund, HealthFundAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(PatientDetail, PatientDetailAdmin)
admin.site.register(PatientConsult, PatientConsultAdmin)
admin.site.register(HerbalMedicine, HerbalMedicineAdmin)
admin.site.register(HerbIndication, HerbIndicationAdmin)
admin.site.register(HerbAction, HerbActionAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(HerbalFormula, HerbalFormulaAdmin)
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(DispensedItem, DispensedItemAdmin)
admin.site.register(ProductStrength, ProductStrengthsAdmin)
admin.site.register(FormulaBottleSize, FormulaBottleSizesAdmin)
admin.site.register(FormulaSetting, FormulaSettingAdmin)