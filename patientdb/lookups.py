from ajax_select import register, LookupChannel
from .models import HerbalMedicine

@register('herbalmedicines')
class HerbMedLookup(LookupChannel):

    model = HerbalMedicine

    def get_query(self, q, request):
          return self.model.objects.filter(herb_name__icontains=q).order_by('herb_name')
    
    def can_add(self, user, model):
        """ customize can_add by allowing anybody to add a Group.
            the superclass implementation uses django's permissions system to check.
            only those allowed to add will be offered a [+ add] popup link
            """
        return True