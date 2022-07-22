from django.urls import path, include
# from django.contrib.auth import views as auth_views
from patientdb import views
from .views import PatientListView, PatientCreateInfoView, ProductListView, FormulaListView, AboutTemplateView, \
    PatientDetailView, FormulaDetailView, HerbMedListView, HerbMedCreateView, HerbIndicationCreateView, HerbIndicationListView, \
    HerbIndicationUpdateView, HerbActionListView, HerbActionCreateView, HerbActionUpdateView, SupplierListView, \
    SupplierCreateView, SupplierUpdateView, BrandListView, BrandCreateView, BrandUpdateView, DispensedItemListView, \
    ProductCreateView, ProductUpdateView, CreatePatientView, ProductRelatedListView, CreateFormulaView, \
    DispensedItemCreateView, HerbMedUpdateView, DispensedItemPreSelectView, FormulaAnalyseView, FormulaSettingsListView, \
    FormulaSettingsCreateView, FormulaSettingsUpdateView, UpdateFormulaView, CloneFormula, PatientFullCreateView, \
    PatientUpdateInfoView, ProductFormSetView, FormulaSettingsFormSetView, BottleSizeListView, BottleSizeCreateView, \
    BottleSizeUpdateView, BottleSizeFormSetView, HealthFundListView, HealthFundCreateView, HealthFundUpdateView, HealthFundFormSetView, \
    ProductStrengthListView, ProductStrengthCreateView, ProductStrengthUpdateView, ProductStrengthFormSetView, SupplierShowProductView, \
    BrandProductsListView, DispensedItemPatientListView, FormulaListPatientView, Pdf, Dispensary_pdf, DispenseTestListView, \
    Dispensaryprint, ChangeHistoryView

from django_filters.views import FilterView
from .filters import PatientConsultFilter

urlpatterns = [

    path('', views.home, name='home'),
    path('cards/', views.cards, name='cards'),
    path('backup/', views.backup, name='backup'),
    # path('print/', views.printlabel, name='printlabel'),
    # PROFILE
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('edit_settings/', views.edit_settings, name='edit_settings'),
    path('about/', AboutTemplateView.as_view(), name='about'),
    # HEALTH FUND
    path('healthfund/list/', HealthFundListView.as_view(), name='healthfund-list'),
    path('healthfund/add/', HealthFundCreateView.as_view(), name='healthfund-add'),
    path('healthfund/update/<int:pk>/', HealthFundUpdateView.as_view(), name='healthfund-update'),
    path('healthfund/formset/view', HealthFundFormSetView.as_view(), name='healthfund-update-grid'),
    # PATIENT
    path('patient/list/', PatientListView.as_view(), name='patient-list'),
    path('patient/add/info/', PatientCreateInfoView.as_view(), name='patient-add-info'),
    path('patient/update/info/<int:pk>/', PatientUpdateInfoView.as_view(), name='patient-update-info'),
    path('patient/add/details/', views.add_patient_details, name='patient-add-details'),
    #path('patient/add/details/', CreatePatientView.as_view(), name='patient-add-details'),
    path('patient/update/details/<int:pk>/', views.edit_patient_details, name='patient-update-details'),
    path('patient/full/', PatientFullCreateView.as_view(), name='patient-full'),
    path('patient/detail/<int:pk>/', PatientDetailView.as_view(), name='patient-detail'),
    path('patient/consult/search/', FilterView.as_view(filterset_class=PatientConsultFilter,
        template_name='patientdb/patient_consult_filter.html'), name='patient-consult-search'),
    # FORMULAS
    path('bottlesize/list/', BottleSizeListView.as_view(), name='bottlesize-list'),
    path('bottlesize/add/', BottleSizeCreateView.as_view(), name='bottlesize-add'),
    path('bottlesize/update/<int:pk>/', BottleSizeUpdateView.as_view(), name='bottlesize-update'),
    path('bottlesize/formset/view', BottleSizeFormSetView.as_view(), name='bottlesize-update-grid'),
    path('formula/list/', FormulaListView.as_view(), name='formula-list'),
    path('formula/patientlist/<int:patient>/', FormulaListPatientView.as_view(), name='formula-patient-list'),
    path('formula/list/<str:options>', FormulaListView.as_view(), name='formula-list'),
    path('formula/detail/<int:pk>/', FormulaDetailView.as_view(), name='formula-detail'),
    path('formula/analyse/<int:pk>/', FormulaAnalyseView.as_view(), name='formula-analyse'),
    path('formula/list/settings/', FormulaSettingsListView.as_view(), name='formula-list-settings'),
    path('formula/add/settings/', FormulaSettingsCreateView.as_view(), name='formula-add-settings'),
    path('formula/settings/view', FormulaSettingsFormSetView.as_view(), name='formula-settings-view'),
    path('formula/update/settings/<int:pk>/', FormulaSettingsUpdateView.as_view(), name='formula-update-settings'),
    #path('formula/create/', FormulaCreateView.as_view(), name='formula-add'),
    path('formula/add/', CreateFormulaView.as_view(), name='formula-add'),
    path('formula/update/<int:pk>/', UpdateFormulaView.as_view(), name='formula-update'),
    path('formula/clone/<int:pk>/', views.CloneFormula, name='formula-clone'),
    path('formula/delete/<int:pk>/', views.DeleteFormula, name='formula-delete'),
    path('formula/get/ingredients/', views.GetFormulaIngredients, name='formula-ingredients'),
    # PRODUCTS
    path('product/list/', ProductListView.as_view(), name='product-list'),
    path('product/formset/view/', ProductFormSetView.as_view(), name='product-view'),
    path('product/add/', ProductCreateView.as_view(), name='product-add'),
    path('product/update/<int:pk>/', ProductUpdateView.as_view(), name='product-update'),
    path('product/related/<int:pk>/<str:herbmedname>/', ProductRelatedListView.as_view(), name='productrelated-list'),
    path('productstrength/list/', ProductStrengthListView.as_view(), name='productstrength-list'),
    path('productstrength/add/', ProductStrengthCreateView.as_view(), name='productstrength-add'),
    path('productstrength/update/<int:pk>/', ProductStrengthUpdateView.as_view(), name='productstrength-update'),
    path('productstrength/formset/view/', ProductStrengthFormSetView.as_view(), name='productstrength-update-grid'),
    # INDICATIONS
    path('indication/list/', HerbIndicationListView.as_view(), name='herbindication-list'),
    path('indication/add/', HerbIndicationCreateView.as_view(), name='herbindication-add'),
    path('indication/ajax/add/', views.AddIndicationAjax, name='herbindication-ajax-add'),
    path('indication/update/<int:pk>/', HerbIndicationUpdateView.as_view(), name='herbindication-update'),
    # ACTIONS
    path('action/list/', HerbActionListView.as_view(), name='herbaction-list'),
    path('action/add/', HerbActionCreateView.as_view(), name='herbaction-add'),
    path('action/update/<int:pk>/', HerbActionUpdateView.as_view(), name='herbaction-update'),
    # SUPPLIERS
    path('supplier/list/', SupplierListView.as_view(), name='supplier-list'),
    path('supplier/show/products/<int:pk>/', SupplierShowProductView.as_view(), name='supplier-show-products'),
    path('supplier/add/', SupplierCreateView.as_view(), name='supplier-add'),
    path('supplier/update/<int:pk>/', SupplierUpdateView.as_view(), name='supplier-update'),
    # BRANDS
    path('brand/list/', BrandListView.as_view(), name='brand-list'),
    path('brand/products/<int:pk>/', BrandProductsListView.as_view(), name='brand-show-products'),
    path('brand/add/', BrandCreateView.as_view(), name='brand-add'),
    path('brand/update/<int:pk>/', BrandUpdateView.as_view(), name='brand-update'),
    # DISPENSED ITEMS
    path('dispensed/list/', DispensedItemListView.as_view(), name='dispensed-list'),
    path('dispensary/print/', Dispensaryprint.as_view(), name='dispensary-print'),
    path('dispensary/pdf/', Dispensary_pdf.as_view(), name='dispensary-pdf'),
    path('dispensary/test/', DispenseTestListView.as_view(), name='dispensary-pdf'),
    path('dispensed/patientlist/<int:patient>/', DispensedItemPatientListView.as_view(), name='dispensed-patientlist'),
    path('dispensed/add/', DispensedItemCreateView.as_view(), name='dispensed-add'),
    path('dispensed/preadd/<int:formula>/<int:patient>/<int:dispensedid>/', DispensedItemPreSelectView.as_view(), name='dispensed-preadd'),
    # HERBAL MEDICINES
    path('herbmed/list/', HerbMedListView.as_view(), name='herbmed-list'),
    path('herbmed/add/', HerbMedCreateView.as_view(), name='herbmed-add'),
    path('herbmed/update/<int:pk>/<str:herbmedname>/', HerbMedUpdateView.as_view(), name='herbmed-update'),
    path('render/pdf/', Dispensary_pdf.as_view()),
    # ACTION HISTORY
    path('change/history/', ChangeHistoryView.as_view(), name='changehistory-list'),
    path('export/', views.export, name='export'),

]