from django.contrib.auth.forms import UserChangeForm
from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, HerbalFormula, Patient, PatientDetail, PatientConsult, HerbIndication, \
    HerbAction, Supplier, Brand, Product, FormulaHerbItem, DispensedItem, HerbalMedicine, FormulaSetting, \
    Settings, HealthFund, FormulaBottleSize, ProductStrength
from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSetFactory

from django.forms.models import inlineformset_factory, BaseInlineFormSet, BaseModelFormSet

from django_select2.forms import ModelSelect2Widget, ModelSelect2MultipleWidget, Select2MultipleWidget
from django.contrib.admin.widgets import FilteredSelectMultiple
from ajax_select import make_ajax_field
from ajax_select.fields import AutoCompleteSelectMultipleField

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset, Field, ButtonHolder, HTML, Div

from django.core.exceptions import ValidationError

from ckeditor_uploader.widgets import CKEditorUploadingWidget


class EditUserForm(UserChangeForm):
    password = forms.CharField(label='', widget=forms.TextInput(attrs={'type': 'hidden'}))
    username = forms.CharField(disabled=True)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password', )


class EditSettingsForm(forms.ModelForm):
    
    class Meta:
        model = Settings
        fields = ('gst_rate', 'apply_gst', 'formula_use_calc_rrp', )


class UserProfileForm(forms.ModelForm):
    abn = forms.CharField(label='ABN', widget=forms.TextInput(attrs={'type':'number'}))
    business_name = forms.CharField(label='Business or Trading Name')
    is_trial = forms.BooleanField(disabled=True, required=False)
    is_subscribed = forms.BooleanField(disabled=True, required=False)
    trial_expiry_date = forms.DateTimeField(disabled=True, required=False)
    subscription_date = forms.DateTimeField(disabled=True, required=False)

    class Meta:
        model = UserProfile
        exclude = ('user', '')


class PatientNewForm(forms.ModelForm):
    date_of_birth = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'id': 'datepicker', 'data-toggle': 'datepicker', 'placeholder': 'DD/MM/YYYY'}), 
        input_formats=['%d/%m/%Y', '%Y-%m-%d'])
    city = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'City, Town or Suburb'}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': '0295555555'}))
    mobile = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': '0405555555'}))
    email = forms.EmailField(required=False, widget=forms.TextInput(attrs={'placeholder': 'bob@myemail.com.au'}))
    address_1 = forms.CharField(label='Address', widget=forms.TextInput(attrs={'placeholder': '1234 Main Rd'}))
    address_2 = forms.CharField(label='Address Line 2', required=False, widget=forms.TextInput(attrs={'placeholder': 'Apartment, studio, floor'}))
    doctor = forms.CharField(label='Doctor', required=False)
    referred_by = forms.CharField(label='Referred By', required=False)
    health_fund = forms.ModelChoiceField(label='Health Fund', required=False, queryset=HealthFund.objects.all())
    health_fund_provider_no = forms.CharField(label='Health Fund Member No.', required=False)

    def __init__(self, *args, **kwargs):
        super(PatientNewForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_errors = True
        self.helper.error_text_inline = True
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('title', css_class='form-group col-md-2 mb-0'),
                Column('first_name', css_class='form-group col-md-4 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'address_1',
            'address_2',
            Row(
                Column('city', css_class='form-group col-md-6 mb-0'),
                Column('state', css_class='form-group col-md-4 mb-0'),
                Column('postcode', css_class='form-group col-md-2 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('phone', css_class='form-group col-md-6 mb-0'),
                Column('mobile', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('date_of_birth', css_class='form-group col-md-4 mb-0'),
                Column('email', css_class='form-group col-md-8 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('referred_by', css_class='form-group col-md-6 mb-0'),
                Column('doctor', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('health_fund', css_class='form-group col-md-6 mb-0'),
                Column('health_fund_provider_no', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
        )

    class Meta:
        model = Patient
        exclude = ('', )


class EditPatientForm(forms.ModelForm):
    date_of_birth = forms.DateField(required=False, widget=forms.TextInput(
        attrs={'id': 'datepicker', 'data-toggle': 'datepicker', 'placeholder': 'DD/MM/YYYY'}), 
        input_formats=['%d/%m/%Y', '%Y-%m-%d'])
    city = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'City, Town or Suburb'}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': '0295555555'}))
    mobile = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': '0405555555'}))
    email = forms.EmailField(required=False, widget=forms.TextInput(attrs={'placeholder': 'bob@myemail.com.au'}))
    address_1 = forms.CharField(label='Address', widget=forms.TextInput(attrs={'placeholder': '1234 Main Rd'}))
    address_2 = forms.CharField(label='Address Line 2', required=False, widget=forms.TextInput(attrs={'placeholder': 'Apartment, studio, floor'}))
    doctor = forms.CharField(label='Doctor', required=False)
    referred_by = forms.CharField(label='Referred By', required=False)
    health_fund = forms.ModelChoiceField(label='Health Fund', required=False, queryset=HealthFund.objects.all())
    health_fund_provider_no = forms.CharField(label='Health Fund Member No.', required=False)

    def __init__(self, *args, **kwargs):
        super(EditPatientForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_errors = True
        self.helper.error_text_inline = True
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('title', css_class='form-group col-md-2 mb-0'),
                Column('first_name', css_class='form-group col-md-4 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'address_1',
            'address_2',
            Row(
                Column('city', css_class='form-group col-md-6 mb-0'),
                Column('state', css_class='form-group col-md-4 mb-0'),
                Column('postcode', css_class='form-group col-md-2 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('phone', css_class='form-group col-md-6 mb-0'),
                Column('mobile', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('date_of_birth', css_class='form-group col-md-4 mb-0'),
                Column('email', css_class='form-group col-md-8 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('referred_by', css_class='form-group col-md-6 mb-0'),
                Column('doctor', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('health_fund', css_class='form-group col-md-6 mb-0'),
                Column('health_fund_provider_no', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
        )

    class Meta:
        model = Patient
        exclude = ('', )


class EditPatientDetailsForm(forms.ModelForm):
    allergies = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 5}))
    medication = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 5}))
    supplements = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 5}))
    surgery = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 5}))
    past_illnesses = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 5}))
    family_history = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 5}))
    weight = forms.DecimalField(label='Weight (kg)', required=False)
    height = forms.DecimalField(label='Height (cm)', required=False)

    def __init__(self, *args, **kwargs):
        super(EditPatientDetailsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_errors = True
        self.helper.error_text_inline = True
        self.helper.form_tag = False

        self.helper.layout = Layout(
            Row(
                Column('marital_status', css_class='form-group col-md-6 mb-0'),
                Column('children', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('occupation', css_class='form-group col-md-6 mb-0'),
                Column('weight', css_class='form-group col-md-3 mb-0'),
                Column('height', css_class='form-group col-md-3 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('allergies', css_class='form-group col-md-6 mb-0'),
                Column('medication', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('supplements', css_class='form-group col-md-6 mb-0'),
                Column('family_history', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('past_illnesses', css_class='form-group col-md-6 mb-0'),
                Column('surgery', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
        )


    class Meta:
        model = PatientDetail
        exclude  = ("patient", )



class EditPatientConsultForm(forms.ModelForm):
    
    class Meta:
        model = PatientConsult
        exclude  = ('', )



class PatientDetailInlineForm(forms.ModelForm):
    allergies = forms.CharField(widget=CKEditorUploadingWidget(), required=False)

    def __init__(self, *args, **kwargs):
        super(PatientDetailInlineForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_errors = True
        self.helper.error_text_inline = True
        self.helper.form_tag = False
        self.helper.form_show_labels = False

    class Meta:
        model = PatientDetail
        exclude = ('', )


class HerbMedNewForm(forms.ModelForm):
    actions_herbmed = forms.ModelMultipleChoiceField(required=False,
        label="Choose Related Herbal Actions", queryset=HerbAction.objects.all(), 
        widget=ModelSelect2MultipleWidget(model=HerbAction, search_fields=['herbaction_name__icontains']),
        help_text= 'Enter one or more actions by selecting them')

    indications_herbmed = forms.ModelMultipleChoiceField(required=False,
        label="Choose Related Herbal Indications", queryset=HerbIndication.objects.all(), 
        widget=ModelSelect2MultipleWidget(model=HerbIndication, search_fields=['herbindication_name__icontains']))
    
    products_herbmed = forms.ModelMultipleChoiceField(required=False,
        label="Choose Related Products", queryset=Product.objects.all(), 
        widget=ModelSelect2MultipleWidget(model=Product, search_fields=['product_name__icontains']))

    def __init__(self, *args, **kwargs):
        super(HerbMedNewForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_errors = True
        self.helper.error_text_inline = True
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('herb_name', css_class='form-group col-md-6 mb-0'),
                Column('herb_botanical_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('herb_description', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('herb_parts_used', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('indications_herbmed', css_class='form-group col-md-11 col-sm-10 mb-0'),
                HTML("""
                    <div class="col-md-1 col-sm-2 pt-4 ">
                         <button id="addIndication" type="button" class="btn shadow-none" data-toggle="modal" 
                                    data-recordtype="Indication" data-target="#addRecordModal">
                            <span data-toggle="tooltip" title="Add New indication" style="font-size: 36px; color: green;">
                                 <i class="fas fa-plus-circle"></i>
                            </span>
                        </button>
                    </div>
                """),
                css_class="form-row"
            ),
            Row(
                Column('actions_herbmed', css_class='form-group col-md-11 col-sm-10 mb-0'),
                HTML("""
                    <div class="col-md-1 col-sm-2 pt-4 ">
                         <button id="addAction" type="button" class="btn shadow-none" data-toggle="modal" 
                                    data-recordtype="Action" data-target="#addRecordModal">
                            <span data-toggle="tooltip" title="Add New Action" style="font-size: 36px; color: green;">
                                 <i class="fas fa-plus-circle"></i>
                            </span>
                        </button>
                    </div>
                """),
                css_class="form-row"
            ),
            Row(
                Column('products_herbmed', css_class='form-group col-md-12 mb-0'),
                css_class="form-row"
            ),
        )

    class Meta:
        model = HerbalMedicine
        exclude = ('', )


class HerbMedUpdateForm(forms.ModelForm):
    actions_herbmed = forms.ModelMultipleChoiceField(
        label="Choose Related Herbal Actions", queryset=HerbAction.objects.all(), 
        widget=ModelSelect2MultipleWidget(model=HerbAction, queryset=HerbAction.objects.all(), search_fields=['herbaction_name__icontains']),
        help_text= 'Enter one or more actions by selecting them', required=False)

    indications_herbmed = forms.ModelMultipleChoiceField(
        label="Choose Related Herbal Indications", queryset=HerbIndication.objects.all(),
        widget=ModelSelect2MultipleWidget(model=HerbIndication, queryset=HerbIndication.objects.all(), search_fields=['herbindication_name__icontains']),
        help_text= 'Enter one or more indications by selecting them', required=False)
    
    products_herbmed = forms.ModelMultipleChoiceField(
        label="Choose Related Products", queryset=Product.objects.all(),
        widget=ModelSelect2MultipleWidget(model=Product, search_fields=['product_name__icontains']),
        help_text= 'Enter one or more related products by selecting them', required=False)

    def __init__(self, *args, **kwargs):
        super(HerbMedUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_errors = True
        self.helper.error_text_inline = True
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('herb_name', css_class='form-group col-md-6 mb-0'),
                Column('herb_botanical_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('herb_description', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('herb_parts_used', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('indications_herbmed', css_class='form-group col-md-11 col-sm-10 mb-0'),
                HTML("""
                    <div class="col-md-1 col-sm-2 pt-4 ">
                         <button id="addIndication" type="button" class="btn shadow-none" data-toggle="modal" 
                                    data-recordtype="Indication" data-target="#addRecordModal">
                            <span data-toggle="tooltip" title="Add New indication" style="font-size: 36px; color: green;">
                                 <i class="fas fa-plus-circle"></i>
                            </span>
                        </button>
                    </div>
                """),
                css_class="form-row"
            ),
            Row(
                Column('actions_herbmed', css_class='form-group col-md-11 col-sm-10 mb-0'),
                HTML("""
                    <div class="col-md-1 col-sm-2 pt-4 ">
                         <button id="addAction" type="button" class="btn shadow-none" data-toggle="modal" 
                                    data-recordtype="Action" data-target="#addRecordModal">
                            <span data-toggle="tooltip" title="Add New Action" style="font-size: 36px; color: green;">
                                 <i class="fas fa-plus-circle"></i>
                            </span>
                        </button>
                    </div>
                """),
                css_class="form-row"
            ),
            Row(
                Column('products_herbmed', css_class='form-group col-md-12 mb-0'),
                css_class="form-row"
            ),
        )

    class Meta:
        model = HerbalMedicine
        exclude = ('', )


class HerbIndicationNewForm(forms.ModelForm):
    herbindication_name = forms.CharField(required=True, help_text = 'Required. Alphanumeric and must be unique',
        label = 'Herb Indication')
    herbmed_indications = forms.ModelMultipleChoiceField(
        label="Choose Related Herbal Medicines", queryset=HerbalMedicine.objects.all(), 
        widget=ModelSelect2MultipleWidget(model=HerbalMedicine, search_fields=['herb_name__icontains']),
        help_text = 'Select one or more herbal medicines with this indication<br />Click in the field to display a list, \
            or type characters to filter the list.<br /> Use ctrl+click to select more than one from the list', required=False)

    class Meta:
        model = HerbIndication
        exclude = ('', )


class HerbIndicationUpdateForm(forms.ModelForm):
    herbindication_name = forms.CharField(required=True, help_text = 'Required. Alphanumeric and must be unique',
        label = 'Herb Indication')
    herbmed_indications = forms.ModelMultipleChoiceField(
        label="Choose Related Herbal Medicines", queryset=HerbalMedicine.objects.all(),
        widget=ModelSelect2MultipleWidget(model=HerbalMedicine, search_fields=['herb_name__icontains']),
        help_text = 'Add or remove one or more herbal medicines with this indication. Click in the field to display a list. \
            <br />Use ctrl+click to select more than one from the list', required=True)

    class Meta:
        model = HerbIndication
        exclude = ('', )


class HerbActionNewForm(forms.ModelForm):
    herbaction_name = forms.CharField(required=True, help_text = 'Required. Alphanumeric and must be unique',
        label = 'Herb Action')
    herbmed_actions = forms.ModelMultipleChoiceField(
        label="Choose Related Herbal Medicines", queryset=HerbalMedicine.objects.all(), 
        widget=ModelSelect2MultipleWidget(model=HerbalMedicine, search_fields=['herb_name__icontains']),
        help_text = 'Select one or more herbal medicines with this action<br />Click in the field to display a list, \
            or type characters to filter the list. <br />Use ctrl+click to select more than one from the list', required=False)
    
    class Meta:
        model = HerbAction
        exclude = ('', )


class HerbActionUpdateForm(forms.ModelForm):
    herbaction_name = forms.CharField(required=True, help_text = 'Required. Alphanumeric and must be unique',
        label = 'Herb Action')

    herbmed_actions = forms.ModelMultipleChoiceField(
        label="Choose Related Herbal Medicines", queryset=HerbalMedicine.objects.all(),
        widget=ModelSelect2MultipleWidget(model=HerbalMedicine, search_fields=['herb_name__icontains']),
        help_text = 'Add or remove one or more herbal medicines with this action. <br />Click in the field to display a list. \
           <br />Use ctrl+click to select more than one from the list', required=True)
     
    class Meta:
        model = HerbAction
        exclude = ('', )
        

class FormulaHerbItemFormSetForm(BaseInlineFormSet):

    def clean(self):
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return

        listofproducts = []
        formulatype = self.data['formula_type']
        percentage = 0

        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            product = form.cleaned_data.get('product')
            quantity = form.cleaned_data.get('quantity')
            if product in listofproducts:
                raise forms.ValidationError("Ingredients cannot be duplicated")
            # percentage formula type must add to 100%
            if formulatype == "P":
                if quantity:
                    percentage = percentage + int(quantity)
            if product:
                listofproducts.append(product)
        
        if formulatype == "P":
            if percentage != 100:
                raise forms.ValidationError("Percentage formula type must have 100 as the total")


class FormulaHerbItemInlineForm(forms.ModelForm):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), widget=ModelSelect2Widget(
            model=Product,
            search_fields=['product_name__icontains']),
            required=True)
    my_default_errors = {
            'required': 'Enter valid numeric value',
            'invalid': 'Enter a valid value'
    }
    """ product = forms.ModelChoiceField(queryset=Product.objects.all(),
            required=True) """
    quantity = forms.DecimalField(required=True, error_messages=my_default_errors)

    def clean_product(self):
        code = self.cleaned_data["product"]
        return code
    
    def clean_quantity(self):
        qty = self.cleaned_data["quantity"]
        try:    
            val = float(qty) 
        except ValueError:    
            raise forms.ValidationError("Quantity must be numeric")
        return qty

    def __init__(self, *args, **kwargs):
        super(FormulaHerbItemInlineForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_errors = True
        self.helper.error_text_inline = True
        self.helper.form_tag = False
        self.helper.form_show_labels = False

    class Meta:
        model = FormulaHerbItem
        exclude = ('', )


class DispensedItemInlineForm(forms.ModelForm):
    """ patient = forms.ModelChoiceField(queryset=Patient.objects.all(), widget=ModelSelect2Widget(
            model=Patient,
            search_fields=['last_name__icontains', 'first_name__icontains']),
            required=False) """
    patient = forms.ModelChoiceField(queryset=Patient.objects.all(),
            required=False) 
    quantity = forms.IntegerField(required=True)
    doseage = forms.DecimalField(required=True, max_digits=4, decimal_places=2)
    frequency = forms.CharField(required=True, max_length=30)
    directions = forms.CharField(required=True, max_length=30)

    def __init__(self, *args, **kwargs):
        super(DispensedItemInlineForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_errors = True
        self.helper.error_text_inline = True
        self.helper.form_tag = False
        self.helper.form_show_labels = True

    class Meta:
        model = DispensedItem
        exclude = ('', )


class FormulaNewForm(forms.ModelForm):

    def clean_formula_code(self):
        code = self.cleaned_data["formula_code"]
        if not code[:1].isalpha():
            raise forms.ValidationError("Formula Code must start with a letter")
        return code

    def clean_formula_type(self):
        type = self.cleaned_data["formula_type"]
        if not type[:1] in "MDPT":
            raise forms.ValidationError("Formula Type must be M, D, P, or T")
        return type

    def __init__(self, *args, **kwargs):
        super(FormulaNewForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_errors = True
        self.helper.error_text_inline = True
        self.helper.form_tag = False
        self.helper.layout = Layout(
                Row(
                    Column('formula_code', css_class='form-group col-md-6 mb-0'),
                    Column('formula_type', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
        )

    class Meta:
        model = HerbalFormula
        exclude = ('patient_formulas', 'formula_ingredients', )


class SupplierNewForm(forms.ModelForm):
    brand_supplier = forms.ModelMultipleChoiceField(queryset=Brand.objects.all(), 
            widget=ModelSelect2MultipleWidget(model=Brand,
            search_fields=['brand_name__icontains']),
            label='Brands available with this supplier', required=False)

    def __init__(self, *args, **kwargs):
        super(SupplierNewForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_errors = True
        self.helper.error_text_inline = True
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('supplier_name', css_class='form-group col-md-8 mb-0'),
                Column('supplier_customer_code', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            'address_1',
            'address_2',
            Row(
                Column('city', css_class='form-group col-md-6 mb-0'),
                Column('state', css_class='form-group col-md-4 mb-0'),
                Column('postcode', css_class='form-group col-md-2 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('phone', css_class='form-group col-md-4 mb-0'),
                Column('email', css_class='form-group col-md-8 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('supplier_rep', css_class='form-group col-md-6 mb-0'),
                Column('mobile', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('brand_supplier', css_class='form-group col-md-12 mb-0'),
            ),
            Submit('submit', 'Add Supplier', css_class='btn-block')
        )

    class Meta:
        model = Supplier
        exclude = ('', )


class SupplierUpdateForm(forms.ModelForm):
    brand_supplier = forms.ModelMultipleChoiceField(queryset=Brand.objects.all(), widget=ModelSelect2MultipleWidget(
            model=Brand, 
            search_fields=['brand_name__icontains']),
            label='Brands available with this supplier', required=True)
    
    def __init__(self, *args, **kwargs):
        super(SupplierUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_errors = True
        self.helper.error_text_inline = True
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('supplier_name', css_class='form-group col-md-8 mb-0'),
                Column('supplier_customer_code', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            'address_1',
            'address_2',
            Row(
                Column('city', css_class='form-group col-md-6 mb-0'),
                Column('state', css_class='form-group col-md-4 mb-0'),
                Column('postcode', css_class='form-group col-md-2 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('phone', css_class='form-group col-md-4 mb-0'),
                Column('email', css_class='form-group col-md-8 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('supplier_rep', css_class='form-group col-md-6 mb-0'),
                Column('mobile', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('brand_supplier', css_class='form-group col-md-12 mb-0'),
            ),
            Submit('submit', 'Update Supplier', css_class='btn-block')
        )

    class Meta:
        model = Supplier
        exclude = ('', )


class ProductNewForm(forms.ModelForm):
    herbmed_product = forms.ModelMultipleChoiceField(queryset=HerbalMedicine.objects.all(), widget=ModelSelect2MultipleWidget(
            model=HerbalMedicine, 
            search_fields=['herb_name__icontains']),
            label='Related herbal medicines', required=True)
    
    product_brand = forms.ModelChoiceField(queryset=Brand.objects.all(), widget=ModelSelect2Widget(
            model=Brand, 
            search_fields=['brand_name__icontains']),
            label='Related brand', required=True)
 
    def __init__(self, *args, **kwargs):
        super(ProductNewForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_errors = True
        self.helper.error_text_inline = True
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('product_name', css_class='form-group col-md-8 mb-0'),
                Column('product_code', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('product_strength', css_class='form-group col-md-4 mb-0'),
                Column('product_qty', css_class='form-group col-md-4 mb-0'),
                Column('product_unit', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('product_cost', css_class='form-group col-md-12 mb-0'),
            ),
            Row(
                Column('product_dose', css_class='form-group col-md-12 mb-0'),
            ),
            Row(
                Column('product_brand', css_class='form-group col-md-12 mb-0'),
            ),
            Row(
                Column('herbmed_product', css_class='form-group col-md-12 mb-0'),
            ),
        )

    class Meta:
        model = Product
        exclude = ('', )


class ProductUpdateForm(forms.ModelForm):
    herbmed_product = forms.ModelMultipleChoiceField(queryset=HerbalMedicine.objects.all(), widget=ModelSelect2MultipleWidget(
            model=HerbalMedicine, 
            search_fields=['herb_name__icontains']),
            label='Related herbal medicines', required=True)

    product_brand = forms.ModelChoiceField(queryset=Brand.objects.all(), widget=ModelSelect2Widget(
            model=Brand, 
            search_fields=['brand_name__icontains']),
            label='Related brand', required=True)

    def __init__(self, *args, **kwargs):
        super(ProductUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_errors = True
        self.helper.error_text_inline = True
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('product_name', css_class='form-group col-md-8 mb-0'),
                Column('product_code', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('product_strength', css_class='form-group col-md-4 mb-0'),
                Column('product_qty', css_class='form-group col-md-4 mb-0'),
                Column('product_unit', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('product_cost', css_class='form-group col-md-12 mb-0'),
            ),
            Row(
                Column('product_dose', css_class='form-group col-md-12 mb-0'),
            ),
            Row(
                Column('product_brand', css_class='form-group col-md-12 mb-0'),
            ),
            Row(
                Column('herbmed_product', css_class='form-group col-md-12 mb-0'),
            ),
        )

    class Meta:
        model = Product
        exclude = ('', )


class BrandNewForm(forms.ModelForm):
    supplier_brand = forms.ModelMultipleChoiceField(queryset=Supplier.objects.all(), widget=ModelSelect2MultipleWidget(
            model=Supplier,
            search_fields=['supplier_name__icontains']), required=False)

    class Meta:
        model = Brand
        exclude = ('', )


class BrandUpdateForm(forms.ModelForm):
    supplier_brand = forms.ModelMultipleChoiceField(queryset=Supplier.objects.all(), widget=ModelSelect2MultipleWidget(
            model=Supplier,
            search_fields=['supplier_name__icontains']), label='Suppliers of this brand', required=True)

    class Meta:
        model = Brand
        exclude = ('', )


class DispensedItemNewForm(forms.ModelForm):
    # patient = forms.ModelChoiceField(queryset=Patient.objects.order_by('last_name'))
    patient = forms.ModelChoiceField(queryset=Patient.objects.all(), 
            widget=ModelSelect2Widget(model=Patient,
            search_fields=['last_name__icontains', 'first_name__icontains', 'address_1__icontains']),
            label='Patient Name', required=True)
    
    # formula = forms.ModelChoiceField(queryset=HerbalFormula.objects.order_by('formula_code'))
    formula = forms.ModelChoiceField(queryset=HerbalFormula.objects.all(), widget=ModelSelect2Widget(
            model=HerbalFormula, 
            search_fields=['formula_code__icontains']), label='Formula Code', required=True)
    
    doseage = forms.DecimalField(required=True, widget=forms.TextInput(attrs={'placeholder': '5'}))
    administerin = forms.CharField(required=True, label='Administer', widget=forms.TextInput(attrs={'placeholder': 'in water or juice'}))

    def __init__(self, *args, **kwargs):
        super(DispensedItemNewForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_errors = True
        self.helper.error_text_inline = True
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'patient',
            'formula',
            Row(
                Column('quantity', css_class='form-group col-md-6 mb-0'),
                Column('qtytype', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('doseage', css_class='form-group col-md-2 mb-0'),
                Column('measure', css_class='form-group col-md-2 mb-0'),
                Column('administerin', css_class='form-group col-md-4 mb-0'),
                Column('frequency', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            'directions',
        )

    class Meta:
        model = DispensedItem
        ordering = ['-modified']
        exclude = ('', )
        labels = {
            'measure': 'Dose Unit',
            'qtytype': 'Unit Size',
        }


class DispensedItemPreSelectForm(forms.ModelForm):
    # this form enables preselection of formula code and patient - called from formula list
    patient = forms.ModelChoiceField(queryset=Patient.objects.all(), widget=ModelSelect2Widget(
            model=Patient,
            search_fields=['last_name__icontains', 'first_name__icontains', 'address_1__icontains']),
            label='Patient Name', required=True)
    
    formula = forms.ModelChoiceField(queryset=HerbalFormula.objects.all(), widget=ModelSelect2Widget(
            model=HerbalFormula, search_fields=['formula_code__icontains']), 
            label='Formula Code', required=True)
    
    doseage = forms.DecimalField(required=True, widget=forms.TextInput(attrs={'placeholder': '5'}))
    administerin = forms.CharField(required=True, label='Administer', widget=forms.TextInput(attrs={'placeholder': 'in water or juice'}))

    class Meta:
        model = DispensedItem
        ordering = ['-modified']
        exclude = ('', )
        labels = {
            'measure': 'Dose Unit',
            'qtytype': 'Unit Size',
        }

    # we set up initial fields depending on the information passed
    # use the formula id to reference select list initial formula code value
    def __init__(self, formula=0, patient=0, dispensedid=0, *args, **kwargs):
        super(DispensedItemPreSelectForm, self).__init__(*args,**kwargs)
        # formulaid passed on the url so set initial value in modelchoicefield 'formula' above
        if formula != 0:
            self.fields['formula'].initial = formula

        if patient != 0:
            self.fields['patient'].initial = patient
            
        # if dispenseditem id is passed then prefill form fields with the dispensed item details
        if dispensedid != 0:
            dispensed = DispensedItem.objects.get(pk=dispensedid)
            self.fields['quantity'].initial = dispensed.quantity
            self.fields['qtytype'].initial = dispensed.qtytype
            self.fields['doseage'].initial = dispensed.doseage
            self.fields['measure'].initial = dispensed.measure
            self.fields['frequency'].initial = dispensed.frequency
            self.fields['administerin'].initial = dispensed.administerin
            self.fields['directions'].initial = dispensed.directions

        # crispy form setup
        self.helper = FormHelper()
        self.helper.form_show_errors = True
        self.helper.error_text_inline = True
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'patient',
            'formula',
            Row(
                Column('quantity', css_class='form-group col-md-6 mb-0'),
                Column('qtytype', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('doseage', css_class='form-group col-md-2 mb-0'),
                Column('measure', css_class='form-group col-md-2 mb-0'),
                Column('administerin', css_class='form-group col-md-4 mb-0'),
                Column('frequency', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            'directions',
        ) 


class FormulaAnalyseForm(forms.Form):
    bottle_sizes = forms.ModelChoiceField(queryset=FormulaSetting.objects.all(), initial=7)


class ProductFormSetFormView(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ProductFormSetFormView, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_errors = True
        self.helper.error_text_inline = True
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('product_name', css_class='form-group col-md-4 mb-0'),
                Column('product_code', css_class='form-group col-md-2 mb-0'),
                Column('product_qty', css_class='form-group col-md-2 mb-0'),
                Column('product_unit', css_class='form-group col-md-2 mb-0'),
                Column('product_cost', css_class='form-group col-md-2 mb-0'),
                css_class='form-row'
            ),
        )

        self.newhelper = FormHelper()
        self.newhelper.form_show_errors = True
        self.newhelper.error_text_inline = True
        self.newhelper.form_tag = False
        self.newhelper.form_show_labels = False
        self.newhelper.layout = Layout(
            Row(
                Column('product_name', css_class='form-group col-md-4 mb-0'),
                Column('product_code', css_class='form-group col-md-2 mb-0'),
                Column('product_qty', css_class='form-group col-md-2 mb-0'),
                Column('product_unit', css_class='form-group col-md-2 mb-0'),
                Column('product_cost', css_class='form-group col-md-2 mb-0'),
                css_class='form-row'
            ),
        )
    
    class Meta:
        model = Product
        fields = ['product_name', 'product_code', 'product_qty', 'product_unit', 'product_cost']


class ProductFormSetClass(BaseModelFormSet):

    def clean(self):
        print("In formset clean")
        if any(self.errors):
            raise forms.ValidationError("Validation errors: " + str(self.errors))

        for form in self.forms:
            print(form)
        
    class Meta:
        model = Product
        fields = ['product_name', 'product_code', 'product_qty', 'product_unit', 'product_cost']


class CustomCheckbox(Field):
    template = 'patientdb/custom_checkbox.html'

class FormulaSettingsFormSetFormView(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(FormulaSettingsFormSetFormView, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_errors = True
        self.helper.error_text_inline = True
        self.helper.form_tag = False
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Row(
                Column('formula_bottle_size', css_class='form-group col-md-3 mb-0'),
                Column('formula_bottle_cost', css_class='form-group col-md-1 mb-0'),
                Column('formula_bottle_size_mu', css_class='form-group col-md-2 mb-0'),
                Column('formula_bottle_size_min_rrp', css_class='form-group col-md-2 mb-0'),
                Column('formula_dispensing_fee', css_class='form-group col-md-2 mb-0'),
                #Column('DELETE', css_class='form-group col-md-2 mb-0'),
                CustomCheckbox('DELETE'), 
                css_class='form-row'
            ),
        )

        self.newhelper = FormHelper()
        self.newhelper.form_show_errors = True
        self.newhelper.error_text_inline = True
        self.newhelper.form_tag = False
        self.newhelper.form_show_labels = False
        self.newhelper.layout = Layout(
            Row(
                Column('formula_bottle_size', css_class='form-group col-md-3 mb-0'),
                Column('formula_bottle_cost', css_class='form-group col-md-1 mb-0'),
                Column('formula_bottle_size_mu', css_class='form-group col-md-2 mb-0'),
                Column('formula_bottle_size_min_rrp', css_class='form-group col-md-2 mb-0'),
                Column('formula_dispensing_fee', css_class='form-group col-md-2 mb-0'),
                #Column('DELETE', css_class='form-group col-md-2 mb-0'),
                CustomCheckbox('DELETE'),
                css_class='form-row'
            ),
        )
    
    class Meta:
        model = FormulaSetting
        fields = '__all__'
        labels = {
            'formula_bottle_size': 'Bottle Size',
            'formula_bottle_cost': 'Bottle Cost',
            'formula_bottle_size_mu': 'Formula Markup',
            'formula_bottle_size_min_rrp': 'Minimum RRP',
            'formula_dispensing_fee': 'Dispensing Fee',
            #'DELETE': '',
        }


class FormulaSettingsFormSetClass(BaseModelFormSet):

    def clean(self):
        if any(self.errors):
            raise forms.ValidationError("Validation errors: " + str(self.errors))
        """ 
        for form in self.forms:
            print(form) """
        
    class Meta:
        model = FormulaSetting
        fields = '__all__'


class BottleSizeNewForm(forms.ModelForm):
 
    class Meta:
        model = FormulaBottleSize
        exclude = ('', )


class BottleSizeFormSetFormView(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(BottleSizeFormSetFormView, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_errors = True
        self.helper.error_text_inline = True
        self.helper.form_tag = False
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Row(
                Column('bottle_size', css_class='form-group col-md-3 mb-0'),
                Column('bottle_unit', css_class='form-group col-md-3 mb-0'),
                Column('bottle_notes', css_class='form-group col-md-4 mb-0'),
                CustomCheckbox('DELETE'), 
                css_class='form-row'
            ),
        )

        self.newhelper = FormHelper()
        self.newhelper.form_show_errors = True
        self.newhelper.error_text_inline = True
        self.newhelper.form_tag = False
        self.newhelper.form_show_labels = False
        self.newhelper.layout = Layout(
            Row(
                Column('bottle_size', css_class='form-group col-md-3 mb-0'),
                Column('bottle_unit', css_class='form-group col-md-3 mb-0'),
                Column('bottle_notes', css_class='form-group col-md-4 mb-0'),
                CustomCheckbox('DELETE'), 
                css_class='form-row'
            ),
        )
    
    class Meta:
        model = FormulaBottleSize
        fields = '__all__'
        labels = {
            'bottle_size': 'Bottle Size',
            'bottle_unit': 'Bottle Measure',
            'bottle_notes': 'Notes',
            #'DELETE': '',
        }


class BottleSizeFormSetClass(BaseModelFormSet):

    def clean(self):
        if any(self.errors):
            raise forms.ValidationError("Validation errors: " + str(self.errors))
        """ 
        for form in self.forms:
            print(form) """
        
    class Meta:
        model = FormulaBottleSize
        fields = '__all__'


class HealthFundNewForm(forms.ModelForm):
 
    class Meta:
        model = HealthFund
        exclude = ('', )


class HealthFundFormSetFormView(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(HealthFundFormSetFormView, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_errors = True
        self.helper.error_text_inline = True
        self.helper.form_tag = False
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Row(
                Column('fund_name', css_class='form-group col-md-4 mb-0'),
                Column('provider_no', css_class='form-group col-md-4 mb-0'),
                CustomCheckbox('DELETE'), 
                css_class='form-row'
            ),
        )

        self.newhelper = FormHelper()
        self.newhelper.form_show_errors = True
        self.newhelper.error_text_inline = True
        self.newhelper.form_tag = False
        self.newhelper.form_show_labels = False
        self.newhelper.layout = Layout(
            Row(
                Column('fund_name', css_class='form-group col-md-4 mb-0'),
                Column('provider_no', css_class='form-group col-md-4 mb-0'),
                CustomCheckbox('DELETE'), 
                css_class='form-row'
            ),
        )
    
    class Meta:
        model = HealthFund
        fields = '__all__'
        labels = {
            'fund_name': 'Health Fund Name',
            'provider_no': 'Provider No.',
            #'DELETE': '',
        }


class HealthFundFormSetClass(BaseModelFormSet):

    def clean(self):
        if any(self.errors):
            raise forms.ValidationError("Validation errors: " + str(self.errors))
        """ 
        for form in self.forms:
            print(form) """
        
    class Meta:
        model = HealthFund
        fields = '__all__'


class ProductStrengthNewForm(forms.ModelForm):
 
    class Meta:
        model = ProductStrength
        exclude = ('', )


class ProductStrengthFormSetFormView(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(ProductStrengthFormSetFormView, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_errors = True
        self.helper.error_text_inline = True
        self.helper.form_tag = False
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Row(
                Column('strength', css_class='form-group col-md-4 mb-0'),
                Column('notes', css_class='form-group col-md-4 mb-0'),
                CustomCheckbox('DELETE'), 
                css_class='form-row'
            ),
        )

        self.newhelper = FormHelper()
        self.newhelper.form_show_errors = True
        self.newhelper.error_text_inline = True
        self.newhelper.form_tag = False
        self.newhelper.form_show_labels = False
        self.newhelper.layout = Layout(
            Row(
                Column('strength', css_class='form-group col-md-4 mb-0'),
                Column('notes', css_class='form-group col-md-4 mb-0'),
                CustomCheckbox('DELETE'), 
                css_class='form-row'
            ),
        )
    
    class Meta:
        model = ProductStrength
        fields = '__all__'
        labels = {
            'strength': 'Extract Strength',
            'notes': 'Notes',
            #'DELETE': '',
        }


class ProductStrengthFormSetClass(BaseModelFormSet):

    def clean(self):
        if any(self.errors):
            raise forms.ValidationError("Validation errors: " + str(self.errors))
        """ 
        for form in self.forms:
            print(form) """
        
    class Meta:
        model = ProductStrength
        fields = '__all__'