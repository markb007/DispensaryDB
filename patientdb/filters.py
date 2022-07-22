import django_filters
from .models import PatientConsult

class PatientConsultFilter(django_filters.FilterSet):
    patient_consult__first_name = django_filters.CharFilter(lookup_expr='icontains')
    patient_consult__last_name = django_filters.CharFilter(lookup_expr='icontains')
    summary = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = PatientConsult
        fields = '__all__'