# Create your views here.
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.contrib import messages
from .forms import EditUserForm, UserProfileForm, PatientNewForm,\
        EditPatientForm, EditPatientDetailsForm, EditPatientConsultForm, HerbIndicationNewForm, HerbIndicationUpdateForm, \
        HerbActionNewForm, HerbActionUpdateForm, SupplierNewForm, SupplierUpdateForm, BrandNewForm, \
        BrandUpdateForm, ProductNewForm, ProductUpdateForm, FormulaNewForm, HerbMedNewForm, DispensedItemNewForm, \
        HerbMedUpdateForm, DispensedItemPreSelectForm, FormulaAnalyseForm, FormulaHerbItemInlineForm, DispensedItemInlineForm, \
        FormulaHerbItemFormSetForm, EditSettingsForm, PatientDetailInlineForm, ProductFormSetFormView, ProductFormSetClass, \
        FormulaSettingsFormSetClass, FormulaSettingsFormSetFormView, BottleSizeNewForm, BottleSizeFormSetFormView, \
        BottleSizeFormSetClass, HealthFundNewForm, HealthFundFormSetFormView, HealthFundFormSetClass, ProductStrengthNewForm, \
        ProductStrengthFormSetFormView, ProductStrengthFormSetClass
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.contrib.postgres.search import SearchVector
from django.db.models import Q, Count

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic import CreateView, FormView
from django.views.generic.edit import UpdateView
from django.views.generic.base import TemplateView, TemplateResponseMixin, ContextMixin
from django.views.generic import View  

from django.forms import formset_factory, modelformset_factory

from .models import Patient, PatientDetail, PatientConsult, Product, HerbalFormula, DispensedItem, FormulaHerbItem, \
    HerbalMedicine, HerbIndication, HerbAction, Supplier, Brand, FormulaSetting, Settings, FormulaBottleSize, HealthFund, \
    ProductStrength, UserProfile, ChangeHistory

from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSetFactory, ModelFormSetView
from extra_views import NamedFormsetsMixin
from extra_views.contrib.mixins import SuccessMessageWithInlinesMixin

from django.http import HttpResponseRedirect

# caching
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from django.conf import settings
CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

import re
import datetime
from datetime import timedelta, date, datetime
from django.utils.timezone import make_aware

from django.db.models import Sum

from django.core import management
from django.core.management.commands import dumpdata

from django.core import serializers
from django.db import connection
from .render import Render

from .resources import HerbalFormulaResource

def home(request):
    return render(request, 'patientdb/home.html', {})


def export(request):
    herbal_resource = HerbalFormulaResource()
    dataset = herbal_resource.export()
    dataset.csv
    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="herbalformula.csv"'

    return response


def cards(request):
    return render(request, 'patientdb/testresponsive.html', {})

# create history of actions for create/update/delete on table entries
def create_recent_actions_list(url, detail, username, typeofrequest, modelname):
    new_entry = ChangeHistory(full_url=url, request_data=detail, username=username, \
        request_type=typeofrequest, modelname=modelname)
    new_entry.save()
    return

@login_required
def backup(request):
    messages.success(request, ('Backup complete !!!'))
    management.call_command('dumpdata', exclude=['auth'], output='dbbackup3')
    return redirect('home')


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, ('Logged In !!!'))
            return redirect('home')
        else:
            messages.warning(request, ('Error logging in - please try again !!!'))
            return redirect('login')
    else:
        return redirect('login')


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = EditUserForm(request.POST, instance=request.user)
        pform = UserProfileForm(request.POST, instance=request.user.userprofile)
        if form.is_valid() and pform.is_valid():
            form.save()
            pform.save()
            messages.success(request, ('Profile Updated !!!'))
            return redirect('home')
        else:
            messages.warning(request, ('Please correct the errors below'))
    else:
        form = EditUserForm(instance=request.user)
        pform = UserProfileForm(instance=request.user.userprofile)

    context = {'form': form, 'pform': pform}
    return render(request, 'patientdb/edit_profile.html', context)


@login_required
def edit_settings(request):
    # get the settings record
    settings_exists = Settings.objects.all().count()
    # create record if it doesn't exist
    if settings_exists == 0:
        c = Settings(gst_rate=10.00, apply_gst=True, formula_use_calc_rrp=True)
        c.save()
    
    settings = Settings.objects.all()[:1].get()

    if request.method == "POST":
        form = EditSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, ('Settings Updated !!!'))
            return redirect('home')
        else:
            messages.warning(request, ('Please correct the errors below'))
    else:
        form = EditSettingsForm(instance=settings)

    context = {'form': form}
    return render(request, 'patientdb/edit_settings.html', context)


#   Clone formula - new formula and ingredients associated with it are copied
#     but no patients or dispensed items are copied
@login_required
def CloneFormula(request, pk):
    # get original formula record data
    record = HerbalFormula.objects.get(formula_id=pk)
    # get formula ingredients queryset
    formulaitems = FormulaHerbItem.objects.filter(formula=pk)
    # save new formula record
    record.formula_id = None
    record.formula_code = record.formula_code + '_COPY'
    record.save()

    # copy the formula ingredients using new 'pk' herbalformula instance
    for formulaitem in formulaitems:
        formulaitem.formula = record
        formulaitem.pk = None
        formulaitem.save()
    
    messages.success(request, 'Formula successfully cloned')

    # now redirect to the formula update page
    return HttpResponseRedirect(reverse_lazy('formula-update', kwargs={'pk':record.formula_id}))


#   Delete formula - can only delete if no dispensed items have been done
#     If deleted, formula, formulaherbitem and patient references are removed
@login_required
def DeleteFormula(request, pk):
    # if any items dispensed for this formula then can't delete
    dispensed = DispensedItem.objects.filter(formula=pk).count()
    if dispensed != 0:
        messages.success(request, 'Formula cannot be deleted - previously allocated and dispensed!!')
        return HttpResponseRedirect(reverse_lazy('formula-list'))

    # delete formula and all references in formulaherbitems table and patient table - on delete cascade
    record = HerbalFormula.objects.get(formula_id=pk)
    record.delete()
    messages.success(request, 'Formula successfully deleted')

    return HttpResponseRedirect(reverse_lazy('formula-list'))


@login_required
def edit_patient_details(request, *args, **kwargs):

    patient = get_object_or_404(Patient, pk=kwargs['pk'])
    try: 
        patientdetail = get_object_or_404(PatientDetail, pk=kwargs['pk'])    
    except:
        patientdetail = PatientDetail(patient=patient)        

    if request.method == "POST":
        form = EditPatientForm(request.POST or None, instance=patient)
        pform = EditPatientDetailsForm(request.POST or None, instance=patientdetail)
        if form.is_valid() and pform.is_valid():
            form.save()
            pform.save()
            messages.success(request, ('Patient Updated !!!'))
            return redirect('patient-list')
        else:
            messages.error(request, ('Please correct the errors below'))
    else:
        form = EditPatientForm(instance=patient)
        pform = EditPatientDetailsForm(instance=patientdetail)

    context = {'form': form, 'pform': pform, 'addorupdate': 'Update' }
    return render(request, 'patientdb/patient_update.html', context)

@login_required
def add_patient_details(request):
    template = 'patientdb/patient_update.html'

    if request.method == "POST":
        form = EditPatientForm(request.POST or None)
        pform = EditPatientDetailsForm(request.POST or None)
        if form.is_valid() and pform.is_valid():
            newpatient = form.save()
            details = pform.save(commit=False)
            # assign patient instance so that primary key is set from saved patient record
            details.patient = newpatient
            details.save()
            messages.success(request, ('Patient Added !!!'))
            return redirect('patient-list')
        else:
            messages.error(request, ('Please correct the errors below'))
    else:
        form = EditPatientForm(request.POST or None)
        pform = EditPatientDetailsForm(request.POST or None)

    context = {"form": form, 'pform': pform, 'addorupdate': 'Add'}

    return render(request, template, context)

""" 
    Called via Ajax from DispensedItem to provide formula ingredients for printing
"""
@login_required
def GetFormulaIngredients(request):
    formula = request.GET.get('formula', None)
    herbitems = FormulaHerbItem.objects.all().select_related('product').filter(formula=formula).order_by('product')
    formulainfo = HerbalFormula.objects.get(pk=formula)
    userdetails = UserProfile.objects.get(user=request.user)
    
    # create data variable first
    data = {}

    # set up business name/address/practitioner etc for label
    data['business_name'] = userdetails.business_name
    data['practitioner'] = str(userdetails.user.first_name) + " " + str(userdetails.user.last_name)
    data['address1'] = userdetails.address_1
    data['address2'] = userdetails.address_2
    data['city'] = userdetails.city
    data['state'] = userdetails.state
    data['postcode'] = userdetails.postcode
    data['provider_name'] = userdetails.provider_name
    data['provider_number'] = userdetails.provider_number
    # set 'mls' or 'drops' to print on label
    if formulainfo.formula_type == "D":
        formulatype = 'drops'
    else:
        formulatype = 'mls'
    
    i = 1
    for e in herbitems:
        keyval = "herb_" + str(i)
        keyval2 = "quantity_" + str(i)
        product = str(e.product)
        quantity = str(e.quantity)
        data[keyval] = product
        data[keyval2] = quantity
        i = i+1

    # create expiry date based on settings
    today = date.today()
    this_month = today.month
    expire_year = today.year + 2

    data['expiry'] = "%s/%s" % (this_month, expire_year)
    data['formulatype'] = formulatype

    return JsonResponse(data, safe=False)


""" 
    Called via Ajax for quickly adding Herbal Indication or Action from Herbal Medicine template
"""
@login_required
def AddIndicationAjax(request):
    dbTable = request.GET.get('addToTable', None)
    addIndication = request.GET.get('dataentry', None)
    
    data = {}
    msg = "Invalid data received"
    pattern = re.compile("[A-Za-z0-9 ]+")

    # check for valid action or indication - not null, first character is a letter, and rest is alphanumeric but space allowed
    if (addIndication and addIndication[0].isalpha() and pattern.fullmatch(addIndication) is not None):
        if (dbTable == "Indication"):
            if HerbIndication.objects.filter(herbindication_name=addIndication).exists():
                msg = "Record already exists"
            else:
                p = HerbIndication(herbindication_name=addIndication)
                p.save()
                msg = "Record added"
        elif (dbTable == "Action"):
            if HerbAction.objects.filter(herbaction_name=addIndication).exists():
                msg = "Record already exists"
            else:
                p = HerbAction(herbaction_name=addIndication)
                p.save()
                msg = "Record added"
        else:
            msg = "Invalid request"
    
    data['outcome'] = msg

    return JsonResponse(data, safe=False)


class AboutTemplateView(TemplateView):
    template_name = "patientdb/about.html"

    def get_context_data(self, *args, **kwargs):
        context = super(AboutTemplateView, self).get_context_data(*args, **kwargs)
        context['title'] = 'Its about us'
        return context


class PatientDetailInline(InlineFormSetFactory):
    fields = '__all__'
    factory_kwargs = {'extra': 1,'max_num': 1, 'can_delete': False, 'can_order': False}
    form_class = PatientDetailInlineForm
    model = PatientDetail
    exclude = ('patient', )


class PatientCreateInfoView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Patient
    model = "Patient"
    form_class = PatientNewForm
    success_url = reverse_lazy('patient-list')
    success_message = "Patient %(first_name)s %(last_name)s was added successfully"
    template_name = 'patientdb/patient_form.html'

    def form_valid(self, form):
        create_recent_actions_list(self.request.build_absolute_uri(), form.instance, self.request.user, "Create", self.__class__.modelname)
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class PatientUpdateInfoView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Patient
    modelname = "Patient"
    form_class = EditPatientForm
    success_url = reverse_lazy('patient-list')
    success_message = "Patient %(first_name)s %(last_name)s was updated successfully"
    template_name = 'patientdb/patient_update_info.html'

    def form_valid(self, form):
        create_recent_actions_list(self.request.build_absolute_uri(), form.instance, self.request.user, "Update", self.__class__.modelname)
        form.instance.modified_by = self.request.user
        return super().form_valid(form)


class PatientFullCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateWithInlinesView):
    model = Patient
    form_class = PatientNewForm
    inlines = [PatientDetailInline]  
    success_url = reverse_lazy('patient-list')
    success_message = "Patient %(first_name)s %(last_name)s was added successfully"
    template_name = 'patientdb/patient_full.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


# create patient with details
class CreatePatientView(LoginRequiredMixin, SuccessMessageMixin, CreateWithInlinesView):
    model = Patient
    form_class = PatientNewForm
    inlines = [PatientDetailInline]  
    template_name = 'patientdb/patient_and_detail.html'
    success_url = reverse_lazy('patient-list')
    success_message = "Patient %(first_name)s %(last_name)s was added successfully"


class PatientListView(LoginRequiredMixin, ListView):

    model = Patient
    paginate_by = 10
    
    def get_paginate_by(self, queryset):
        
        # Paginate by specified value in querystring, or use default class property value.
        
        return self.request.GET.get('paginate_by', self.paginate_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()

        #   adjust items per page display dropdown if necessary - set to string otherwise doesn't match in template
        if (self.request.GET.get('paginate_by') != None):
            context['paginate_by'] = self.request.GET.get('paginate_by')
        else:
            context['paginate_by'] = str(self.paginate_by)
        # keep search value across pages
        if (self.request.GET.get('searchfield1') != None):
            context['searchfieldvalue'] = self.request.GET.get('searchfield1')
        else:
            context['searchfieldvalue'] = ""
        
        context['datefilter'] = self.request.GET.get('optdate')
        context['sortfilter'] = self.request.GET.get('optsort')
            
        return context

    def get_queryset(self):
        field1 = self.request.GET.get('searchfield1')
        datefilter = self.request.GET.get('optdate')
        sortfilter = self.request.GET.get('optsort')
        pl = Patient.objects.all()
        orderbyargs = ['-modified']

        # check if date filter and apply if necessary
        if (datefilter is not None) and (len(datefilter) > 0):
            today = date.today()
            this_month = today.month
            last_month = today.month - 1 if today.month>1 else 12
            change_year = today.year if today.month>1 else today.year - 1
            this_year = today.year
            last_year = this_year - 1
            some_day_last_week = today - timedelta(days=7)
            monday_of_last_week = some_day_last_week - timedelta(days=(some_day_last_week.isocalendar()[2] - 1))
            monday_of_this_week = monday_of_last_week + timedelta(days=7)
            sunday_of_last_week = monday_of_this_week - timedelta(days=1)

            # ok create date filter arguments and pass to query {dictionary: d}
            if datefilter == '1':     # today
                filter_args = {'modified__date': today}
            elif datefilter == '2':   # this week
                filter_args = {'modified__date__gte': monday_of_this_week, 'modified__date__lte': today}
            elif datefilter == '3':   # last week
                filter_args = {'modified__date__gte': monday_of_last_week, 'modified__date__lte': sunday_of_last_week}
            elif datefilter == '4':   # this month
                filter_args = {'modified__month': this_month,'modified__year': this_year }
            elif datefilter == '5':   # last month
                filter_args = {'modified__month': last_month, 'modified__year': change_year }   
            elif datefilter == '6':   # this year
                filter_args = {'modified__year': this_year }   
            elif datefilter == '7':   # last year
                filter_args = {'modified__year': last_year }  
            else:
                filter_args = {}

            filter_args = dict((k,v) for k,v in filter_args.items() if v is not None)
            pl = pl.filter(**filter_args)

        # ok create sort filter arguments if selected and pass to query [list]
        if (sortfilter is not None) and (len(sortfilter) > 0):
            if sortfilter == '1':     # last name
                orderbyargs = ['last_name'] + orderbyargs
            elif sortfilter == '2':   # first name
                orderbyargs = ['first_name'] + orderbyargs
            elif sortfilter == '3':   # city
                orderbyargs = ['city'] + orderbyargs
            elif sortfilter == '4':   # postcode
                orderbyargs = ['postcode'] + orderbyargs
        
        # apply search argument via filter on several fields
        if (field1 is not None) and (len(field1) > 0):
            pl = pl.filter(
                    Q(first_name__icontains=field1) |
                    Q(last_name__icontains=field1) |
                    Q(address_1__icontains=field1) |
                    Q(city__icontains=field1) |
                    Q(mobile__icontains=field1) |
                    Q(email__icontains=field1))

        # now return result set after applying ordering of data
        return pl.order_by(*orderbyargs)


class ProductCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Product
    modelname = "Product" 
    form_class = ProductNewForm
    success_url = reverse_lazy('product-list')
    success_message = "Product %(product_name)s was added successfully"
    template_name = 'patientdb/product_add.html'

    def form_valid(self, form):
        create_recent_actions_list(self.request.build_absolute_uri(), form.instance, self.request.user, "Create", self.__class__.modelname)
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    paginate_by = 10
    
    def get_paginate_by(self, queryset):
        
        # Paginate by specified value in querystring, or use default class property value.
        
        return self.request.GET.get('paginate_by', self.paginate_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()

        #   adjust items per page display dropdown if necessary - set to string otherwise doesn't match in template
        if (self.request.GET.get('paginate_by') != None):
            context['paginate_by'] = self.request.GET.get('paginate_by')
        else:
            context['paginate_by'] = str(self.paginate_by)
        # keep search value across pages
        if (self.request.GET.get('searchfield1') != None):
            context['searchfieldvalue'] = self.request.GET.get('searchfield1')
        else:
            context['searchfieldvalue'] = ""

        return context

    # @cache_page(CACHE_TTL)
    def get_queryset(self):
        field1 = self.request.GET.get('searchfield1')
        pl = Product.objects.all()
        # enable search of product on name, code, and brand
        if field1 is not None:
            return pl.filter(Q(product_name__icontains=field1) |
                    Q(product_code__icontains=field1) |
                    Q(product_brand__brand_name__icontains=field1)).order_by('product_name')
        else:
            return pl.order_by('product_name')


class ProductUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Product
    modelname = "Product"
    form_class = ProductUpdateForm
    success_url = reverse_lazy('product-list')
    success_message = "Product %(product_name)s was updated successfully"
    template_name = 'patientdb/product_update.html'

    def form_valid(self, form):
        # create record to be able to show last 10 create/update/delete actions
        create_recent_actions_list(self.request.build_absolute_uri(), form.instance, self.request.user, "Update", self.__class__.modelname)
        form.instance.modified_by = self.request.user
        return super().form_valid(form)


class HerbMedCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = HerbalMedicine
    model = "HerbalMedicine"
    form_class = HerbMedNewForm
    success_url = reverse_lazy('herbmed-list')
    success_message = "Herbal medicine %(herb_name)s was added successfully"
    template_name = 'patientdb/herbalmedicine_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['herbmed_product'] = HerbalMedicine.objects.all() 
        return context

    def form_valid(self, form):
        create_recent_actions_list(self.request.build_absolute_uri(), form.instance, self.request.user, "Create", self.__class__.modelname)
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class HerbMedUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = HerbalMedicine
    modelname = "HerbalMedicine"
    form_class = HerbMedUpdateForm
    success_url = reverse_lazy('herbmed-list')
    success_message = "Herbal medicine %(herb_name)s was updated successfully"
    template_name = 'patientdb/herbalmedicine_update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['herbmed_product'] = HerbalMedicine.objects.filter(herb_id=self.kwargs['pk']) 
        return context

    def form_valid(self, form):
        create_recent_actions_list(self.request.build_absolute_uri(), form.instance, self.request.user, "Update", self.__class__.modelname)
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class HerbMedListView(LoginRequiredMixin, ListView):
    model = HerbalMedicine
    paginate_by = 10
    
    def get_paginate_by(self, queryset):
        
        # Paginate by specified value in querystring, or use default class property value.
        
        return self.request.GET.get('paginate_by', self.paginate_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()

        #   adjust items per page display dropdown if necessary - set to string otherwise doesn't match in template
        if (self.request.GET.get('paginate_by') != None):
            context['paginate_by'] = self.request.GET.get('paginate_by')
        else:
            context['paginate_by'] = str(self.paginate_by)

        if (self.request.GET.get('searchfield1') != None):
            context['searchfieldvalue'] = self.request.GET.get('searchfield1')
        else:
            context['searchfieldvalue'] = ""

        return context
    
    def get_queryset(self):
        field1 = self.request.GET.get('searchfield1')
        # also annotate herbal medicines with no. of related products
        # pl = HerbalMedicine.objects.all().annotate(products=Count('product__herbmed_product'))
        pl = HerbalMedicine.objects.all().annotate(products=Count('products_herbmed', distinct=True))
        
        if field1 is not None:
            return pl.filter(Q(herb_name__icontains=field1) |
                             Q(herb_botanical_name__icontains=field1) |
                             Q(herb_description__icontains=field1)).order_by('herb_name')
        else:
            return pl.order_by('herb_name')


class FormulaListView(LoginRequiredMixin, ListView):
    model = HerbalFormula
    paginate_by = 10

    def get_paginate_by(self, queryset):
        
        # Paginate by specified value in querystring, or use default class property value.
        
        return self.request.GET.get('paginate_by', self.paginate_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()

        #   adjust items per page display dropdown if necessary - set to string otherwise doesn't match in template
        if (self.request.GET.get('paginate_by') != None):
            context['paginate_by'] = self.request.GET.get('paginate_by')
        else:
            context['paginate_by'] = str(self.paginate_by)

        if (self.request.GET.get('searchfield1') != None):
            context['searchfieldvalue'] = self.request.GET.get('searchfield1')
        else:
            context['searchfieldvalue'] = ""
        
        context['datefilter'] = self.request.GET.get('optdate')
        context['sortfilter'] = self.request.GET.get('optsort')

        return context

    def get_queryset(self):
        field1 = self.request.GET.get('searchfield1')
        datefilter = self.request.GET.get('optdate')
        sortfilter = self.request.GET.get('optsort')
        pl = HerbalFormula.objects.all().annotate(patients=Count('patient_formulas', distinct=True),
                             dispensed=Count('patient_formulas'))
        orderbyargs = ['-modified']
        
        # check if date filter and apply if necessary
        if (datefilter is not None) and (len(datefilter) > 0) and (datefilter != '0'):
            today = date.today()
            this_month = today.month
            last_month = today.month - 1 if today.month>1 else 12
            change_year = today.year if today.month>1 else today.year - 1
            this_year = today.year
            last_year = this_year - 1
            some_day_last_week = today - timedelta(days=7)
            monday_of_last_week = some_day_last_week - timedelta(days=(some_day_last_week.isocalendar()[2] - 1))
            monday_of_this_week = monday_of_last_week + timedelta(days=7)
            sunday_of_last_week = monday_of_this_week - timedelta(days=1)

            # ok create date filter arguments and pass to query {dictionary: d}
            if datefilter == '1':     # today
                filter_args = {'modified__date': today}
            elif datefilter == '2':   # this week
                filter_args = {'modified__date__gte': monday_of_this_week, 'modified__date__lte': today}
            elif datefilter == '3':   # last week
                filter_args = {'modified__date__gte': monday_of_last_week, 'modified__date__lte': sunday_of_last_week}
            elif datefilter == '4':   # this month
                filter_args = {'modified__month': this_month,'modified__year': this_year }
            elif datefilter == '5':   # last month
                filter_args = {'modified__month': last_month, 'modified__year': change_year }   
            elif datefilter == '6':   # this year
                filter_args = {'modified__year': this_year }   
            elif datefilter == '7':   # last year
                filter_args = {'modified__year': last_year }  
            else:
                filter_args = {}

            filter_args = dict((k,v) for k,v in filter_args.items() if v is not None)
            pl = pl.filter(**filter_args)

        # ok create sort filter arguments if selected and pass to query [list]
        if (sortfilter is not None) and (len(sortfilter) > 0) and (sortfilter != '0'):
            if sortfilter == '1':     # formula_code
                orderbyargs = ['formula_code'] + orderbyargs
        
        # apply search argument via filter
        if (field1 is not None) and (len(field1) > 0):
            pl = pl.filter(Q(formula_code__icontains=field1))
        
        # now return result set after applying ordering of data
        return pl.order_by(*orderbyargs)


class FormulaListPatientView(LoginRequiredMixin, ListView):
    model = HerbalFormula
    template_name = "patientdb/formulalistforpatient.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        patient_rec = Patient.objects.get(patientid=self.kwargs['patient'])
        context['patient_name'] = patient_rec.first_name + ' ' + patient_rec.last_name
        return context

    def get_queryset(self):
        field1 = self.request.GET.get('searchfield1')
        datefilter = self.request.GET.get('optdate')
        sortfilter = self.request.GET.get('optsort')
        pl = HerbalFormula.objects.all().filter(patient_formulas=self.kwargs['patient']).distinct(). \
                annotate(patients=Count('patient_formulas', distinct=True),
                             dispensed=Count('patient_formulas'))
        orderbyargs = ['-modified']
        
        # check if date filter and apply if necessary
        if (datefilter is not None) and (len(datefilter) > 0) and (datefilter != '0'):
            today = date.today()
            this_month = today.month
            last_month = today.month - 1 if today.month>1 else 12
            change_year = today.year if today.month>1 else today.year - 1
            this_year = today.year
            last_year = this_year - 1
            some_day_last_week = today - timedelta(days=7)
            monday_of_last_week = some_day_last_week - timedelta(days=(some_day_last_week.isocalendar()[2] - 1))
            monday_of_this_week = monday_of_last_week + timedelta(days=7)
            sunday_of_last_week = monday_of_this_week - timedelta(days=1)

            # ok create date filter arguments and pass to query {dictionary: d}
            if datefilter == '1':     # today
                filter_args = {'modified__date': today}
            elif datefilter == '2':   # this week
                filter_args = {'modified__date__gte': monday_of_this_week, 'modified__date__lte': today}
            elif datefilter == '3':   # last week
                filter_args = {'modified__date__gte': monday_of_last_week, 'modified__date__lte': sunday_of_last_week}
            elif datefilter == '4':   # this month
                filter_args = {'modified__month': this_month,'modified__year': this_year }
            elif datefilter == '5':   # last month
                filter_args = {'modified__month': last_month, 'modified__year': change_year }   
            elif datefilter == '6':   # this year
                filter_args = {'modified__year': this_year }   
            elif datefilter == '7':   # last year
                filter_args = {'modified__year': last_year }  
            else:
                filter_args = {}

            filter_args = dict((k,v) for k,v in filter_args.items() if v is not None)
            pl = pl.filter(**filter_args)

        # ok create sort filter arguments if selected and pass to query [list]
        if (sortfilter is not None) and (len(sortfilter) > 0) and (sortfilter != '0'):
            if sortfilter == '1':     # formula_code
                orderbyargs = ['formula_code'] + orderbyargs
        
        # apply search argument via filter
        if (field1 is not None) and (len(field1) > 0):
            pl = pl.filter(Q(formula_code__icontains=field1))
        
        # now return result set after applying ordering of data
        return pl.order_by(*orderbyargs)


class HerbIndicationCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = HerbIndication
    form_class = HerbIndicationNewForm
    success_url = reverse_lazy('herbindication-list')
    success_message = "Herb indication relationship was added successfully"
    template_name = 'patientdb/herbindication_add.html'

    def post(self, request, *args, **kwargs):
        if "Cancel" in request.POST:
            messages.warning(self.request, 'Operation cancelled')
            return HttpResponseRedirect(reverse_lazy('herbindication-list'))
        elif "Another" in request.POST:
            super(HerbIndicationCreateView, self).post(request, *args, **kwargs)
            return HttpResponseRedirect(reverse_lazy('herbindication-add'))
        else:
            return super(HerbIndicationCreateView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class HerbIndicationListView(LoginRequiredMixin, ListView):
    model = HerbIndication
    paginate_by = 10
    
    def get_paginate_by(self, queryset):
        
        # Paginate by specified value in querystring, or use default class property value.
        
        return self.request.GET.get('paginate_by', self.paginate_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()

        #   adjust items per page display dropdown if necessary - set to string otherwise doesn't match in template
        if (self.request.GET.get('paginate_by') != None):
            context['paginate_by'] = self.request.GET.get('paginate_by')
        else:
            context['paginate_by'] = str(self.paginate_by)
        # keep search value across pages
        if (self.request.GET.get('searchfield1') != None):
            context['searchfieldvalue'] = self.request.GET.get('searchfield1')
        else:
            context['searchfieldvalue'] = ""

        return context
    
    def get_queryset(self):
        field1 = self.request.GET.get('searchfield1')
        pl = HerbIndication.objects.all().annotate(references=Count('herbmed_indications'))
        
        if field1 is not None:
            return pl.filter(Q(herbindication_name__icontains=field1)).order_by('-modified')
        else:
            return pl.order_by('-modified')



class HerbIndicationUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = HerbIndication
    form_class = HerbIndicationUpdateForm
    success_url = reverse_lazy('herbindication-list')
    success_message = "Herb indication relationship was updated successfully"
    template_name = 'patientdb/herbindication_update.html'

    def post(self, request, *args, **kwargs):
        if "Cancel" in request.POST:
            messages.warning(self.request, 'Operation cancelled')
            return HttpResponseRedirect(reverse_lazy('herbindication-list'))
        else:
            return super(HerbIndicationUpdateView, self).post(request, *args, **kwargs)

    def get_queryset(self): 
        return HerbIndication.objects.all().filter(pk=self.kwargs['pk'])


class HerbActionCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = HerbAction
    form_class = HerbActionNewForm
    success_url = reverse_lazy('herbaction-list')
    success_message = "Herb action relationship was added successfully"
    template_name = 'patientdb/herbaction_add.html'

    def post(self, request, *args, **kwargs):
        if "Cancel" in request.POST:
            messages.warning(self.request, 'Operation cancelled')
            return HttpResponseRedirect(reverse_lazy('herbaction-list'))
        elif "Another" in request.POST:
            super(HerbActionCreateView, self).post(request, *args, **kwargs)
            return HttpResponseRedirect(reverse_lazy('herbaction-add'))
        else:
            return super(HerbActionCreateView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class HerbActionListView(LoginRequiredMixin, ListView):
    model = HerbAction
    paginate_by = 10
    
    def get_paginate_by(self, queryset):
        
        # Paginate by specified value in querystring, or use default class property value.
        
        return self.request.GET.get('paginate_by', self.paginate_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()

        #   adjust items per page display dropdown if necessary - set to string otherwise doesn't match in template
        if (self.request.GET.get('paginate_by') != None):
            context['paginate_by'] = self.request.GET.get('paginate_by')
        else:
            context['paginate_by'] = str(self.paginate_by)
        # keep search value across pages
        if (self.request.GET.get('searchfield1') != None):
            context['searchfieldvalue'] = self.request.GET.get('searchfield1')
        else:
            context['searchfieldvalue'] = ""

        return context
    
    def get_queryset(self):
        field1 = self.request.GET.get('searchfield1')
        pl = HerbAction.objects.all().annotate(references=Count('herbmed_actions'))
        
        if field1 is not None:
            return pl.filter(Q(herbaction_name__icontains=field1)).order_by('-modified')
        else:
            return pl.order_by('herbaction_name')


class HerbActionUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = HerbAction
    form_class = HerbActionUpdateForm
    success_url = reverse_lazy('herbaction-list')
    success_message = "Herb action relationship was updated successfully"
    template_name = 'patientdb/herbaction_update.html'

    def post(self, request, *args, **kwargs):
        if "Cancel" in request.POST:
            messages.warning(self.request, 'Operation cancelled')
            return HttpResponseRedirect(reverse_lazy('herbaction-list'))
        else:
            return super(HerbActionUpdateView, self).post(request, *args, **kwargs)

    def get_queryset(self): 
        return HerbAction.objects.all().filter(pk=self.kwargs['pk'])

"""
class PatientUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Patient
    fields = "__all__"
    success_url = reverse_lazy('patient-list')
    success_message = "Patient %(first_name)s %(last_name)s was updated successfully"
    template_name = 'patientdb/patient_update.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super(PatientUpdateView, self).get_context_data(**kwargs)
        context['form'] = Patient.objects.get(pk=self.kwargs['pk'])
        context['pform'] = PatientDetail.objects.get(pk=self.kwargs['pk'])
        return context
"""

class PatientDetailView(LoginRequiredMixin, SuccessMessageMixin, DetailView):

    # get patient record, patient details and patient consult records 
    def get_queryset(self):
        return Patient.objects.all().select_related('patientdetail').filter(pk=self.kwargs['pk']).prefetch_related('consultdetails')


class FormulaDetailView(LoginRequiredMixin, SuccessMessageMixin, DetailView):
    model = HerbalFormula
    template_name = "patientdb/herbalformula_detail.html"

    def get_context_data(self, **kwargs):
        context = super(FormulaDetailView, self).get_context_data(**kwargs)
        # context['totalform'] = FormulaHerbItem.objects.all().filter(formula=self.kwargs['pk']).annotate(totalform=Sum('quantity'))
        formula = HerbalFormula.objects.all().filter(pk=self.kwargs['pk'])
        herbitems = FormulaHerbItem.objects.all().select_related('product').filter(formula=self.kwargs['pk'])
        totals = herbitems.aggregate(sum=Sum('quantity')).get('sum')
        patients = DispensedItem.objects.all().select_related('patient').filter(formula=self.kwargs['pk']) \
                    .annotate(dispensed=Count('patient'))
        
        context = {
            'formula': formula[0],
            'ingredients': herbitems,
            'patients': patients,
            'totalform': totals,
        }

        return context


class FormulaAnalyseView(LoginRequiredMixin, SuccessMessageMixin, DetailView):
    model = HerbalFormula
    template_name = "patientdb/herbalformula_analyse.html"

    def get_context_data(self, **kwargs):
        context = super(FormulaAnalyseView, self).get_context_data(**kwargs)
        if (self.request.GET.get('bottlesize') == None):
            bottlesize = 1
        else:
            bottlesize = int(self.request.GET.get('bottlesize'))

        formula = HerbalFormula.objects.all().filter(pk=self.kwargs['pk'])
        selectedbottle = FormulaSetting.objects.get(formula_settings_id=bottlesize)
        settings = FormulaSetting.objects.all()
        herbitems = FormulaHerbItem.objects.all().select_related('product').filter(formula=self.kwargs['pk']).order_by('product')
        # add up formula total as previously saved
        totalforformula = herbitems.aggregate(sum=Sum('quantity')).get('sum')

        markup = selectedbottle.formula_bottle_size_mu
        minrrp = selectedbottle.formula_bottle_size_min_rrp
        size = selectedbottle.formula_bottle_size.bottle_size

        costperdose = 0.00
        costinformula = [0.00] * len(herbitems)
        i = 0
        formulatype = formula[0].formula_type

        for ingredient in herbitems:
            formulaqty = ingredient.quantity
            productcost = ingredient.product.product_cost
            productsize = ingredient.product.product_qty
            if ingredient.product.product_unit == 'L':
                productsize *= 1000
            
            # get the formula item calculations for the formula type
            formulavalues = calc_formula_costs(formulatype, formulaqty, size, totalforformula, productcost, productsize)
            
            costinformula[i] = formulavalues['costinformula']
            costperdose += float(costinformula[i])
            i += 1

        if formulatype == "M":
            # cost per bottle is the bottle size divided by the formula size multiplied by the cost per dose
            costperbottle = (float(size / totalforformula)) * costperdose
        elif formulatype == "D":
            costperbottle = (float(size * 20 / totalforformula)) * costperdose
        elif formulatype == "P":
            costperbottle = (float(size / totalforformula)) * costperdose
        elif formulatype == "T":
            costperbottle = (float(size / totalforformula)) * costperdose
        else:
            costperbottle = 0.00
            
        # retail at markup for bottle size plus GST
        retailperbottle = costperbottle * ((100.00 + float(markup))/100.00) * 1.10

        context = {
            'formula': formula[0],
            'ingredients': herbitems,
            'totalform': totalforformula,
            'settings': settings,
            'initial': bottlesize,
            'size': size,
            'costinformula': costinformula,
            'costperdose': costperdose,
            'costperbottle': costperbottle,
            'retailperbottle': retailperbottle,
            'minrrp': minrrp,
            'markup': markup,
        }

        return context


def calc_formula_costs(formulatype, formulaqty, bottlesize, totals, productcost, productsize):
    formulavalues = {}
    if formulatype == "M":
        # cost in formula is price per ml x no. of mls for the item
        formulavalues['priceperml'] = productcost / productsize
        formulavalues['costinformula'] = formulavalues['priceperml'] * formulaqty
    elif formulatype == "D":
        formulavalues['priceperml'] = productcost / productsize
        # cost in the formula is price per drop x no. of drops
        formulavalues['costinformula'] = (formulavalues['priceperml'] / 20) * formulaqty
    elif formulatype == "P":
        # cost in formula is price per ml x percentage of this item in the formula
        formulavalues['priceperml'] = productcost / productsize
        formulavalues['costinformula'] = formulavalues['priceperml'] * formulaqty 
    elif formulatype == "T":
        # cost in formula is price per ml x total mls
        formulavalues['priceperml'] = productcost / productsize
        formulavalues['costinformula'] = formulavalues['priceperml'] * formulaqty
    else:
        # formulatype invalid
        formulavalues['priceperml'] = 0.00
        formulavalues['costinformula'] = 0.00

    return formulavalues


class FormulaSettingsListView(LoginRequiredMixin, ListView):
    model = FormulaSetting
    paginate_by = 10
    fields = "__all__"
    order_by = 'id'
    template_name = 'patientdb/formula_list_settings.html'


class FormulaSettingsCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = FormulaSetting
    fields = "__all__"
    success_url = reverse_lazy('formula-list-settings')
    success_message = "Formula setting was added successfully"
    template_name = 'patientdb/formula_add_settings.html'


class FormulaSettingsUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = FormulaSetting
    fields = "__all__"
    success_url = reverse_lazy('formula-list-settings')
    success_message = "Formula setting was updated successfully"
    template_name = 'patientdb/formula_update_settings.html'


class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier
    paginate_by = 10
    
    def get_paginate_by(self, queryset):
        
        # Paginate by specified value in querystring, or use default class property value.
        
        return self.request.GET.get('paginate_by', self.paginate_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()

        #   adjust items per page display dropdown if necessary - set to string otherwise doesn't match in template
        if (self.request.GET.get('paginate_by') != None):
            context['paginate_by'] = self.request.GET.get('paginate_by')
        else:
            context['paginate_by'] = str(self.paginate_by)
        # keep search value across pages
        if (self.request.GET.get('searchfield1') != None):
            context['searchfieldvalue'] = self.request.GET.get('searchfield1')
        else:
            context['searchfieldvalue'] = ""
            
        return context
    
    def get_queryset(self):
        field1 = self.request.GET.get('searchfield1')
        pl = Supplier.objects.all().annotate(references=Count('supplierbrand'))
        
        if field1 is not None:
            return pl.filter(Q(supplier_name__icontains=field1)).order_by('supplier_name')
        else:
            return pl.order_by('supplier_name')


# TODO
class SupplierShowProductView(LoginRequiredMixin, ListView):
    model = Supplier
    paginate_by = 10

  
class SupplierCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Supplier
    form_class = SupplierNewForm
    success_url = reverse_lazy('supplier-list')
    success_message = "Supplier was added successfully"
    template_name = 'patientdb/supplier_add.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class SupplierUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Supplier
    form_class = SupplierUpdateForm
    success_url = reverse_lazy('supplier-list')
    success_message = "Supplier %(supplier_name)s was updated successfully"
    template_name = 'patientdb/supplier_update.html'

    def get_queryset(self): 
        return Supplier.objects.all().filter(pk=self.kwargs['pk'])


class BrandListView(LoginRequiredMixin, ListView):
    model = Brand
    paginate_by = 10
    
    def get_paginate_by(self, queryset):
        
        # Paginate by specified value in querystring, or use default class property value.
        
        return self.request.GET.get('paginate_by', self.paginate_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()

        #   adjust items per page display dropdown if necessary - set to string otherwise doesn't match in template
        if (self.request.GET.get('paginate_by') != None):
            context['paginate_by'] = self.request.GET.get('paginate_by')
        else:
            context['paginate_by'] = str(self.paginate_by)
        # keep search value across pages
        if (self.request.GET.get('searchfield1') != None):
            context['searchfieldvalue'] = self.request.GET.get('searchfield1')
        else:
            context['searchfieldvalue'] = ""
            
        return context
    
    def get_queryset(self):
        field1 = self.request.GET.get('searchfield1')
        #pl = Brand.objects.all().distinct(references=Count('supplier_brand'), products=Count('product__product_brand'))
        pl = Brand.objects.all().annotate(references=Count('supplier_brand', distinct=True), products=Count('productbrand', distinct=True))
        
        if field1 is not None:
            return pl.filter(Q(brand_name__icontains=field1)).order_by('brand_name')
        else:
            return pl.order_by('brand_name')


class BrandProductsListView(LoginRequiredMixin, ListView):
    model = Product
    paginate_by = 10

    def get_queryset(self):
        brandkey = self.kwargs['pk']
        pl = Product.objects.all().filter(product_brand=brandkey)
        return pl


class BrandCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Brand
    form_class = BrandNewForm
    success_url = reverse_lazy('brand-list')
    success_message = "Brand %(brand_name)s was added successfully"
    template_name = 'patientdb/brand_add.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class BrandUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Brand
    form_class = BrandUpdateForm
    success_url = reverse_lazy('brand-list')
    success_message = "Brand %(brand_name)s was updated successfully"
    template_name = 'patientdb/brand_update.html'


class DispensedItemCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = DispensedItem
    form_class = DispensedItemNewForm
    success_url = reverse_lazy('dispensed-list')
    success_message = "Formula was dispensed successfully"
    template_name = 'patientdb/dispenseditem_add.html'

    def post(self, request, *args, **kwargs):
        if "Cancel" in request.POST:
            return HttpResponseRedirect(reverse_lazy('dispensed-list'))
        elif "Another" in request.POST:
            super(DispensedItemCreateView, self).post(request, *args, **kwargs)
            return HttpResponseRedirect(reverse_lazy('dispensed-add'))
        else:
            return super(DispensedItemCreateView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class DispensedItemListView(LoginRequiredMixin, ListView):
    model = DispensedItem
    template_name = 'patientdb/dispenseditem_list.html'
    paginate_by = 10

    def get_paginate_by(self, queryset):
        
        # Paginate by specified value in querystring, or use default class property value.
        
        return self.request.GET.get('paginate_by', self.paginate_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()

        #   adjust items per page display dropdown if necessary - set to string otherwise doesn't match in template
        if (self.request.GET.get('paginate_by') != None):
            context['paginate_by'] = self.request.GET.get('paginate_by')
        else:
            context['paginate_by'] = str(self.paginate_by)
        # keep search value across pages
        if (self.request.GET.get('searchfield1') != None):
            context['searchfieldvalue'] = self.request.GET.get('searchfield1')
        else:
            context['searchfieldvalue'] = ""
        
        context['datefilter'] = self.request.GET.get('optdate')
        context['sortfilter'] = self.request.GET.get('optsort')
            
        return context
    
    def get_queryset(self):
        field1 = self.request.GET.get('searchfield1')
        datefilter = self.request.GET.get('optdate')
        sortfilter = self.request.GET.get('optsort')
        pl = DispensedItem.objects.all()
        orderbyargs = ['-modified']

        # check if date filter and apply if necessary
        if (datefilter is not None) and (len(datefilter) > 0) and (datefilter != '0'):
            today = date.today()
            this_month = today.month
            last_month = today.month - 1 if today.month>1 else 12
            change_year = today.year if today.month>1 else today.year - 1
            this_year = today.year
            last_year = this_year - 1
            some_day_last_week = today - timedelta(days=7)
            monday_of_last_week = some_day_last_week - timedelta(days=(some_day_last_week.isocalendar()[2] - 1))
            monday_of_this_week = monday_of_last_week + timedelta(days=7)
            sunday_of_last_week = monday_of_this_week - timedelta(days=1)

            # ok create date filter arguments and pass to query {dictionary: d}
            # use only date portion of datetime when comparing
            if datefilter == '1':     # today
                filter_args = {'modified__date': today}
            elif datefilter == '2':   # this week
                filter_args = {'modified__date__gte': monday_of_this_week, 'modified__date__lte': today}
            elif datefilter == '3':   # last week
                filter_args = {'modified__date__gte': monday_of_last_week, 'modified__date__lte': sunday_of_last_week}
            elif datefilter == '4':   # this month
                filter_args = {'modified__month': this_month,'modified__year': this_year }
            elif datefilter == '5':   # last month
                filter_args = {'modified__month': last_month, 'modified__year': change_year }   
            elif datefilter == '6':   # this year
                filter_args = {'modified__year': this_year }   
            elif datefilter == '7':   # last year
                filter_args = {'modified__year': last_year }  
            else:
                filter_args = {}

            filter_args = dict((k,v) for k,v in filter_args.items() if v is not None)
            pl = pl.filter(**filter_args)
         
        # ok create sort filter arguments if selected and pass to query [list]
        if (sortfilter is not None) and (len(sortfilter) > 0) and (sortfilter != '0'):
            if sortfilter == '1':     # formula code
                orderbyargs = ['formula__formula_code'] + orderbyargs
            elif sortfilter == '2':   # last name
                orderbyargs = ['patient__last_name'] + orderbyargs
            elif sortfilter == '3':   # city
                orderbyargs = ['patient__first_name'] + orderbyargs

        # Search field using formula foreign key back to HerbalFormula table and formula_code field
        if (field1 is not None) and (len(field1) > 0):
            pl = pl.filter(
                    Q(formula__formula_code__icontains=field1) |
                    Q(patient__first_name__icontains=field1) |
                    Q(patient__last_name__icontains=field1))
             
        # now return result set after applying ordering of data
        return pl.order_by(*orderbyargs)


class DispensedItemPatientListView(LoginRequiredMixin, ListView):
    model = DispensedItem
    template_name = 'patientdb/dispensedlistforpatient.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        patient_rec = Patient.objects.get(patientid=self.kwargs['patient'])
        context['patient_name'] = patient_rec.first_name + ' ' + patient_rec.last_name
        return context
    
    def get_queryset(self):
        field1 = self.request.GET.get('searchfield1')
        datefilter = self.request.GET.get('optdate')
        sortfilter = self.request.GET.get('optsort')
        pl = DispensedItem.objects.all().filter(patient=self.kwargs['patient'])
        orderbyargs = ['-modified']

        # check if date filter and apply if necessary
        if (datefilter is not None) and (len(datefilter) > 0) and (datefilter != '0'):
            today = date.today()
            this_month = today.month
            last_month = today.month - 1 if today.month>1 else 12
            change_year = today.year if today.month>1 else today.year - 1
            this_year = today.year
            last_year = this_year - 1
            some_day_last_week = today - timedelta(days=7)
            monday_of_last_week = some_day_last_week - timedelta(days=(some_day_last_week.isocalendar()[2] - 1))
            monday_of_this_week = monday_of_last_week + timedelta(days=7)
            sunday_of_last_week = monday_of_this_week - timedelta(days=1)

            # ok create date filter arguments and pass to query {dictionary: d}
            # use only date portion of datetime when comparing
            if datefilter == '1':     # today
                filter_args = {'modified__date': today}
            elif datefilter == '2':   # this week
                filter_args = {'modified__date__gte': monday_of_this_week, 'modified__date__lte': today}
            elif datefilter == '3':   # last week
                filter_args = {'modified__date__gte': monday_of_last_week, 'modified__date__lte': sunday_of_last_week}
            elif datefilter == '4':   # this month
                filter_args = {'modified__month': this_month,'modified__year': this_year }
            elif datefilter == '5':   # last month
                filter_args = {'modified__month': last_month, 'modified__year': change_year }   
            elif datefilter == '6':   # this year
                filter_args = {'modified__year': this_year }   
            elif datefilter == '7':   # last year
                filter_args = {'modified__year': last_year }  
            else:
                filter_args = {}

            filter_args = dict((k,v) for k,v in filter_args.items() if v is not None)
            pl = pl.filter(**filter_args)
         
        # ok create sort filter arguments if selected and pass to query [list]
        if (sortfilter is not None) and (len(sortfilter) > 0) and (sortfilter != '0'):
            if sortfilter == '1':     # formula code
                orderbyargs = ['formula__formula_code'] + orderbyargs
            elif sortfilter == '2':   # last name
                orderbyargs = ['patient__last_name'] + orderbyargs
            elif sortfilter == '3':   # city
                orderbyargs = ['patient__first_name'] + orderbyargs

        # Search field using formula foreign key back to HerbalFormula table and formula_code field
        if (field1 is not None) and (len(field1) > 0):
            pl = pl.filter(
                    Q(formula__formula_code__icontains=field1) |
                    Q(patient__first_name__icontains=field1) |
                    Q(patient__last_name__icontains=field1))
             
        # now return result set after applying ordering of data
        return pl.order_by(*orderbyargs)


class ProductDetailInline(InlineFormSetFactory):
    # set validation to make sure at least one form's fields are filled in
    factory_kwargs = {'extra': 3, 'max_num': 8, 'min_num': 1, 'validate_min': True, 'can_delete': True, 'can_order': False}
    model = FormulaHerbItem
    form_class = FormulaHerbItemInlineForm
    formset_class = FormulaHerbItemFormSetForm
    prefix = 'formulaherbitem_set'
    fields = '__all__'


class ProductDetailInlineUpdate(InlineFormSetFactory):
    # change 'extra' argument so that no extra are displayed for update but you can still add ingredients
    factory_kwargs = {'extra': 0, 'max_num': 8, 'min_num': 1, 'validate_min': True, 'can_delete': True, 'can_order': False}
    model = FormulaHerbItem
    form_class = FormulaHerbItemInlineForm
    formset_class = FormulaHerbItemFormSetForm
    prefix = 'formulaherbitem_set'
    fields = '__all__'


class AllocatedToDetailInline(InlineFormSetFactory):
    factory_kwargs = {'extra': 1, 'max_num': 1, 'can_delete': True, 'can_order': False}
    model = DispensedItem
    form_class = DispensedItemInlineForm
    prefix = 'formulap'
    fields = '__all__'


class CreateFormulaView(LoginRequiredMixin, SuccessMessageWithInlinesMixin, NamedFormsetsMixin, CreateWithInlinesView):
    model = HerbalFormula
    form_class = FormulaNewForm
    # inlines = [ProductDetailInline, AllocatedToDetailInline]
    inlines = [ProductDetailInline]
    # --->> these are the names to render inside the template rather than 'inlines'
    # inlines_names = ['ingredient_form', 'patient_form', ]
    inlines_names = ['ingredient_form', ]
    template_name = 'patientdb/herbalformula_add.html'
    success_url = reverse_lazy('formula-list')
    success_message = "Formula %(formula_code)s was added successfully"

    def post(self, request, *args, **kwargs):
        formula_code = request.POST['formula_code']
        if "Cancel" in request.POST:
            messages.warning(self.request, 'Operation cancelled')
            return HttpResponseRedirect(reverse_lazy('formula-list'))
        elif "Another" in request.POST:
            super(CreateFormulaView, self).post(request, *args, **kwargs)
            return HttpResponseRedirect(reverse_lazy('formula-add'))
        elif "Dispense" in request.POST:
            super(CreateFormulaView, self).post(request, *args, **kwargs)
            formula = HerbalFormula.objects.get(formula_code=formula_code)
            formula.formula_id
            return HttpResponseRedirect(reverse_lazy('dispensed-preadd', kwargs={'formula': formula.formula_id, 'patient': 0, 'dispensedid': 0}))
        else:
            return super(CreateFormulaView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        # form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_message(self, cleaned_data):
        #  cleaned_data is the cleaned data from the form which is used for string formatting
        return self.success_message % cleaned_data


class UpdateFormulaView(LoginRequiredMixin, SuccessMessageWithInlinesMixin, NamedFormsetsMixin, UpdateWithInlinesView):
    model = HerbalFormula
    form_class = FormulaNewForm
    inlines = [ProductDetailInlineUpdate]
    inlines_names = ['ingredient_form']
    template_name = 'patientdb/herbalformula_add.html'
    success_url = reverse_lazy('formula-list')
    success_message = "Formula %(formula_code)s was updated successfully"

    def post(self, request, *args, **kwargs):
        if "Cancel" in request.POST:
            messages.warning(self.request, 'Operation cancelled')
            return HttpResponseRedirect(reverse_lazy('formula-list'))
        else:
            return super(UpdateFormulaView, self).post(request, *args, **kwargs)

    # check if dispensed items
    def get(self, *args, **kwargs):
        dispensed = DispensedItem.objects.filter(formula=kwargs['pk']).count()
        # don't allow update of formula if there are dispensed items
        if dispensed != 0:
            messages.warning(self.request, 'Formula cannot be updated - previously allocated and dispensed!!')
            return HttpResponseRedirect(reverse_lazy('formula-list'))

        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Update'
        return context

    def form_valid(self, form):
        # form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_success_message(self, cleaned_data):
        #  cleaned_data is the cleaned data from the form which is used for string formatting
        return self.success_message % cleaned_data


class ProductRelatedListView(LoginRequiredMixin, ListView):
    model = Product
    paginate_by = 10
    template_name = 'patientdb/productrelated_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['herbmedname'] = self.kwargs['herbmedname']
        return context
    
    def get_queryset(self):
        field1 = self.request.GET.get('searchfield1')
        herbmedkey = self.kwargs['pk']
        pl = Product.objects.filter(herbmed_product__pk=herbmedkey)
        if field1 is not None:
            return pl.filter(Q(product_name__icontains=field1) |
                    Q(product_code__icontains=field1) |
                    Q(product_brand__brand_name__icontains=field1)).order_by('product_name')

        return pl.order_by('product_name')


class DispensedItemPreSelectView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = DispensedItem
    form_class = DispensedItemPreSelectForm
    success_url = reverse_lazy('dispensed-list')
    success_message = "Formula was dispensed successfully"
    template_name = 'patientdb/dispenseditem_add.html'

    def post(self, request, *args, **kwargs):
        if "Cancel" in request.POST:
            messages.warning(self.request, 'Operation cancelled')
            return HttpResponseRedirect(reverse_lazy('dispensed-list'))
        elif "Another" in request.POST:
            super(DispensedItemPreSelectView, self).post(request, *args, **kwargs)
            return HttpResponseRedirect(reverse_lazy('dispensed-preadd', kwargs={'formula': 0, 'patient': 0, 'dispensedid': 0}))
        else:
            return super(DispensedItemPreSelectView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(DispensedItemPreSelectView, self).get_form_kwargs()
        # update the kwargs for the form init method with our url parms
        kwargs.update(self.kwargs)  # self.kwargs contains all url conf params
        return kwargs


class ProductFormSetView(LoginRequiredMixin, SuccessMessageMixin, ModelFormSetView):
    model = Product
    form_class = ProductFormSetFormView
    formset_class = ProductFormSetClass
    template_name = 'patientdb/product_formset.html'
    factory_kwargs = {'extra': 0, 'max_num': 1000,
                      'can_order': False, 'can_delete': False} 
    success_url = reverse_lazy('home')
    success_message = "Products updated successfully"
    fields = ['product_name', 'product_code', 'product_qty', 'product_unit', 'product_cost']

    def formset_valid(self, formset):
        # do whatever you'd like to do with the valid formset
        success_message = self.get_success_message(formset)
        if success_message:
            messages.success(self.request, success_message)
        return super(ProductFormSetView, self).formset_valid(formset)
    
    def formset_invalid(self, formset):
        # do whatever you'd like to do with the valid formset
        return super(ProductFormSetView, self).formset_invalid(formset)

    def get_success_message(self, formset):
        # Here you can use the formset in the message if required
        return str(sum(form.has_changed() for form in formset)) + ' product(s) updated'


class FormulaSettingsFormSetView(LoginRequiredMixin, SuccessMessageMixin, ModelFormSetView):
    model = FormulaSetting
    form_class = FormulaSettingsFormSetFormView
    formset_class = FormulaSettingsFormSetClass
    template_name = 'patientdb/formulasettings_formset.html'
    factory_kwargs = {'extra': 2, 'max_num': 100,
                      'can_order': False, 'can_delete': True} 
    success_url = reverse_lazy('home')
    fields = '__all__'

    def formset_valid(self, formset):
        # do whatever you'd like to do with the valid formset
        success_message = self.get_success_message(formset)
        if success_message:
            messages.success(self.request, success_message)
        return super(FormulaSettingsFormSetView, self).formset_valid(formset)
    
    def formset_invalid(self, formset):
        # do whatever you'd like to do with the valid formset
        return super(FormulaSettingsFormSetView, self).formset_invalid(formset)

    def get_success_message(self, formset):
        # Here you can use the formset in the message if required
        return str(sum(form.has_changed() for form in formset)) + ' setting(s) updated'


class BottleSizeListView(LoginRequiredMixin, ListView):
    model = FormulaBottleSize
    template_name = 'patientdb/bottlesize_list.html'


class BottleSizeCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = FormulaBottleSize
    template_name = 'patientdb/bottlesize_add.html'
    form_class = BottleSizeNewForm
    success_url = reverse_lazy('bottlesize-list')
    success_message = "Bottle size was added successfully"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class BottleSizeUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = FormulaBottleSize
    template_name = 'patientdb/bottlesize_update.html'
    form_class = BottleSizeNewForm
    success_url = reverse_lazy('bottlesize-list')
    success_message = "Bottle size was updated successfully"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class BottleSizeFormSetView(LoginRequiredMixin, SuccessMessageMixin, ModelFormSetView):
    model = FormulaBottleSize
    form_class = BottleSizeFormSetFormView
    formset_class = BottleSizeFormSetClass
    template_name = 'patientdb/bottlesize_formset.html'
    factory_kwargs = {'extra': 2, 'max_num': 30,
                      'can_order': False, 'can_delete': True} 
    success_url = reverse_lazy('home')
    fields = '__all__'

    def formset_valid(self, formset):
        # do whatever you'd like to do with the valid formset
        success_message = self.get_success_message(formset)
        if success_message:
            messages.success(self.request, success_message)
        return super(BottleSizeFormSetView, self).formset_valid(formset)
    
    def formset_invalid(self, formset):
        # do whatever you'd like to do with the valid formset
        return super(BottleSizeFormSetView, self).formset_invalid(formset)

    def get_success_message(self, formset):
        # Here you can use the formset in the message if required
        return str(sum(form.has_changed() for form in formset)) + ' setting(s) updated'


class HealthFundListView(LoginRequiredMixin, ListView):
    model = HealthFund
    template_name = 'patientdb/healthfund_list.html'
    paginate_by = 10

    def get_paginate_by(self, queryset):
        
        # Paginate by specified value in querystring, or use default class property value.
        
        return self.request.GET.get('paginate_by', self.paginate_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()

        #   adjust items per page display dropdown if necessary - set to string otherwise doesn't match in template
        if (self.request.GET.get('paginate_by') != None):
            context['paginate_by'] = self.request.GET.get('paginate_by')
        else:
            context['paginate_by'] = str(self.paginate_by)
        # keep search value across pages
        if (self.request.GET.get('searchfield1') != None):
            context['searchfieldvalue'] = self.request.GET.get('searchfield1')
        else:
            context['searchfieldvalue'] = ""
            
        return context

    def get_queryset(self):
        field1 = self.request.GET.get('searchfield1')
        
        pl = HealthFund.objects.all()
        
        if field1 is not None:
            return pl.filter(Q(fund_name__icontains=field1)).order_by('fund_name')
        else:
            return pl.order_by('fund_name')


class HealthFundCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = HealthFund
    template_name = 'patientdb/healthfund_add.html'
    form_class = HealthFundNewForm
    success_url = reverse_lazy('healthfund-list')
    success_message = "Health Fund was added successfully"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class HealthFundUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = HealthFund
    template_name = 'patientdb/healthfund_update.html'
    form_class = HealthFundNewForm
    success_url = reverse_lazy('healthfund-list')
    success_message = "Health Fund was updated successfully"

    def form_valid(self, form):
        form.instance.modified_by = self.request.user
        return super().form_valid(form)


class HealthFundFormSetView(LoginRequiredMixin, SuccessMessageMixin, ModelFormSetView):
    model = HealthFund
    form_class = HealthFundFormSetFormView
    formset_class = HealthFundFormSetClass
    template_name = 'patientdb/healthfund_formset.html'
    factory_kwargs = {'extra': 2, 'max_num': 30,
                      'can_order': False, 'can_delete': True} 
    success_url = reverse_lazy('home')
    fields = '__all__'

    def formset_valid(self, formset):
        # do whatever you'd like to do with the valid formset
        success_message = self.get_success_message(formset)
        if success_message:
            messages.success(self.request, success_message)
        return super(HealthFundFormSetView, self).formset_valid(formset)
    
    def formset_invalid(self, formset):
        # do whatever you'd like to do with the valid formset
        return super(HealthFundFormSetView, self).formset_invalid(formset)

    def get_success_message(self, formset):
        # Here you can use the formset in the message if required
        return str(sum(form.has_changed() for form in formset)) + ' setting(s) updated'


class ProductStrengthListView(LoginRequiredMixin, ListView):
    model = ProductStrength
    template_name = 'patientdb/productstrength_list.html'


class ProductStrengthCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = ProductStrength
    template_name = 'patientdb/productstrength_add.html'
    form_class = ProductStrengthNewForm
    success_url = reverse_lazy('productstrength-list')
    success_message = "Product Strength was added successfully"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ProductStrengthUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = ProductStrength
    template_name = 'patientdb/productstrength_update.html'
    form_class = ProductStrengthNewForm
    success_url = reverse_lazy('productstrength-list')
    success_message = "Product Strength was updated successfully"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ProductStrengthFormSetView(LoginRequiredMixin, SuccessMessageMixin, ModelFormSetView):
    model = ProductStrength
    form_class = ProductStrengthFormSetFormView
    formset_class = ProductStrengthFormSetClass
    template_name = 'patientdb/productstrength_formset.html'
    factory_kwargs = {'extra': 2, 'max_num': 30,
                      'can_order': False, 'can_delete': True} 
    success_url = reverse_lazy('home')
    fields = '__all__'

    def formset_valid(self, formset):
        # do whatever you'd like to do with the valid formset
        success_message = self.get_success_message(formset)
        if success_message:
            messages.success(self.request, success_message)
        return super(ProductStrengthFormSetView, self).formset_valid(formset)
    
    def formset_invalid(self, formset):
        # do whatever you'd like to do with the valid formset
        return super(ProductStrengthFormSetView, self).formset_invalid(formset)

    def get_success_message(self, formset):
        # Here you can use the formset in the message if required
        return str(sum(form.has_changed() for form in formset)) + ' setting(s) updated'


class Pdf(View):
    template_name = "patientdb/pdf.html"

    def get(self, request):
        patients = Patient.objects.all()
        today = timezone.now()
        params = {
            'today': today,
            'patient_list': patients,
            'request': request
        }
        return Render.render('patientdb/pdf.html', params)


class Dispensary_pdf(View):
    template_name = "patientdb/dispensary_pdf.html"

    def get(self, request):
        """         dispensed = DispensedItem.objects.select_related('formula', 'patient').all() """       
        dispensed = DispensedItem.objects.prefetch_related('formula', 'formula__formula_ingredients', 'formula__formulaherbitem_set').all()
        
        today = timezone.now()
        params = {
            'today': today,
            'dispenseditem_list': dispensed,
            'request': request
        }
        return Render.render('patientdb/dispensary_pdf.html', params)


class DispenseTestListView(LoginRequiredMixin, ListView):
    model = DispensedItem
    template_name = 'patientdb/dispensary_pdf.html'
    
    def get_queryset(self):
        # pl = DispensedItem.objects.prefetch_related('formula', 'formula__formula_ingredients').all()
        pl = DispensedItem.objects.raw('SELECT * FROM DispensedItem')
        return pl

#   Reports

def dictfetchall(cursor):
    #Return all rows from a cursor as a dict
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

class Dispensaryprint(View):

    def get(self, request):
        
        with connection.cursor() as c:
            c.execute('SELECT distinct on (D.id) D.*, H."FormulaCode", array_agg(FHI."quantity") as quantities, array_agg(PR."ProductName") as products, \
                            sum(FHI."quantity") as formulatotal, \
                            array_agg(PR."product_brand_id") as brands, array_agg(PR."product_strength_id") as productstrength, \
                            array_agg(B."BrandAbbrev") as brandabbrev, array_agg(PS."Strength") as strength, \
                            array_agg(distinct concat(P."FirstName", chr(32), P."LastName")) as patientname, count(FHI.formula_id) as numherbs, \
                            array_agg(P."Address1") as patientaddress1, \
                            array_agg(distinct concat(P."City", chr(32), P."State", chr(32), P."PostCode")) as patientcity, \
                            array_agg(distinct(H."FormulaType")) as formulatype \
                        FROM public."DispensedItems" D \
                        left join "HerbalFormulas" H on D."formula_id" = H."FormulaId" \
                        inner join "FormulaHerbItems" FHI on H."FormulaId" = FHI."formula_id" \
                        inner join "Products" PR on PR."ProductId" = FHI.product_id \
                        inner join "Brands" B on PR.product_brand_id = B."BrandId" \
                        inner join "ProductStrengths" PS on PS."id" = PR.product_strength_id \
                        inner join "Patients" P on P."PatientId" = D.patient_id \
                        group by d.id, H."FormulaCode"')
            results = dictfetchall(c)

        today = timezone.now()
        params = {
            'today': today,
            'dispenseditems': results,
            'request': request
        }
        
        return Render.render('patientdb/dispensaryprint.html', params)


class ChangeHistoryView(LoginRequiredMixin, ListView):
    model = ChangeHistory
    template_name = 'patientdb/change_history_list.html'
    paginate_by = 10
    order_by = '-created'
    fields = '__all__'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["changes"] = ChangeHistory.objects.all().order_by('-created')[:10] 
        return context
    