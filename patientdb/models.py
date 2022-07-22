from django.db import models

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

STATE_CHOICES = (('NSW', 'NSW'), ('VIC','VIC'), ('QLD', 'QLD'), ('SA', 'SA'), ('WA', 'WA'), ('NT', 'NT'), ('TAS', 'TAS'))


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides selfupdating ``created`` and ``modified`` fields.
    This is passed to all other models here in order to crate/update timestamps automatically
    """
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

        
class UserProfile(models.Model):
    """
    we extend Django's User model with a one-to-one relationship, add extra fields 
    to the user profile we need
    """
    PROVIDERS = (
        ('ATMS', 'ATMS'),
        ('NHAA', 'NHAA'),
        ('ANTA', 'ANTA'),
        ('CMA', 'CMA'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(db_column='BusinessName', max_length=50, blank=True, null=True)
    abn = models.CharField(max_length=11, db_column='ABN', blank=True, null=True)
    address_1 = models.CharField(db_column='Address1', max_length=50)
    address_2 = models.CharField(db_column='Address2', max_length=50, blank=True, null=True)
    city = models.CharField(db_column='City', max_length=20)
    state = models.CharField(db_column='State', max_length=3, choices=STATE_CHOICES, default='NSW')
    postcode = models.CharField(db_column='PostCode', max_length=4)
    phone = models.CharField(db_column='Phone', max_length=10, blank=True, null=True)
    mobile = models.CharField(db_column='Mobile', max_length=10, blank=True, null=True)
    provider_name = models.CharField(db_column='ProviderName', max_length=20, default='ATMS')
    provider_number = models.CharField(db_column='ProviderNumber', max_length=20, default='0000')

    is_trial = models.BooleanField(db_column='Is_Trial', default=False, blank=True, null=True)
    is_subscribed = models.BooleanField(db_column='Is_Subscribed', default=False, blank=True, null=True)
    trial_expiry_date = models.DateTimeField(db_column='Trial_Expiry_Date', blank=True, null=True, auto_now=False, auto_now_add=False)
    subscription_date = models.DateTimeField(db_column='Subscription_Date', blank=True, null=True, auto_now=False, auto_now_add=False)

    class Meta:
        managed = True
        db_table = 'UserProfile'
    
    def __str__(self):
        return '%s %s' % (self.user.first_name, self.user.last_name)

#   Signals defined to allow update of extended user profile information when User is updated
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()


class Settings(TimeStampedModel):
    BOOL_CHOICES = ((True, 'Yes'), (False, 'No'))
    apply_gst = models.BooleanField(choices=BOOL_CHOICES, default=True)
    gst_rate = models.name = models.DecimalField(max_digits=4, decimal_places=2, default=10.00)
    formula_use_calc_rrp = models.BooleanField(choices=BOOL_CHOICES, default=True)

    class Meta:
        managed = True
        db_table = 'Settings'


class ChangeHistory(TimeStampedModel):
    full_url = models.CharField(db_column='URL', max_length=50)
    request_data = models.CharField(db_column='RequestData', max_length=30)
    username = models.CharField(db_column='Username', max_length=50)
    request_type = models.CharField(db_column='RequestType', max_length=10)
    modelname = models.CharField(db_column='ModelName', max_length=20)
    
    class Meta:
        managed = True
        db_table = 'ChangeHistory'
        ordering = ['-created']


class Patient(TimeStampedModel):
    """
    Define the patient details table - inherits two timestamp fields from abstract class TimeStampedModel
    """
    TITLE_CHOICES = (('Mr', 'Mr'), ('Mrs','Mrs'), ('Ms', 'Miss'), ('Dr', 'Dr'), ('Esq', 'Esquire'), ('Jr', 'Junior'), 
                      ('Prof', 'Professor'))

    patientid = models.AutoField(db_column='PatientId', primary_key=True)
    title = models.CharField(db_column='Title', max_length=4, choices=TITLE_CHOICES, default='Mr')                                  
    first_name = models.CharField(db_column='FirstName', max_length=50) 
    last_name = models.CharField(db_column='LastName', max_length=50) 
    address_1 = models.CharField(db_column='Address1', max_length=50) 
    address_2 = models.CharField(db_column='Address2', max_length=50, blank=True, null=True)
    city = models.CharField(db_column='City', max_length=20)
    state = models.CharField(db_column='State', max_length=3, choices=STATE_CHOICES, default='NSW') 
    postcode = models.CharField(db_column='PostCode', max_length=4)
    date_of_birth = models.DateField(db_column='DateOfBirth', blank=True, null=True)
    phone = models.CharField(db_column='Phone', max_length=13, blank=True, null=True)
    email = models.EmailField(db_column='Email', max_length=100, blank=True, null=True)
    mobile = models.CharField(db_column='Mobile', max_length=12, blank=True, null=True)
    doctor = models.CharField(db_column='Doctor', max_length=50, blank=True, null=True)
    referred_by = models.CharField(db_column='ReferredBy', max_length=50, blank=True, null=True)
    #health_fund = models.CharField(db_column='HealthFund', max_length=20, blank=True, null=True)
    health_fund = models.ForeignKey('HealthFund', on_delete=models.CASCADE, blank=True, null=True)
    health_fund_provider_no = models.CharField(db_column='HealthFundProviderNo', max_length=20, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Patients'
        ordering = ['last_name']

    def __str__(self):
        #return '%s %s' % (self.first_name, self.last_name)
        return '%s %s %s' % (self.last_name, ',', self.first_name)

    @property
    def full_name(self):
        "Returns the person's full name."
        return '%s %s %s' % (self.title, self.first_name, self.last_name)


class PatientDetail(TimeStampedModel):
    """
    Patient details that are not needed to be loaded every time
    """
    MARITAL_CHOICES = (('M', 'Married'), ('S','Single'), ('D', 'Divorced'), ('SP', 'Separated'), ('W', 'Widowed'), ('RNS', 'Rather not say'),
                            ('DF', 'De Facto'), ('NA', 'Not Applicable'), ('NM', 'Never Married')) 

    patient = models.OneToOneField(Patient, primary_key=True, on_delete=models.CASCADE)
    marital_status = models.CharField(db_column='MaritalStatus', max_length=3, choices=MARITAL_CHOICES, default='NA')
    children = models.IntegerField(db_column='Children', default=0)
    weight = models.DecimalField(db_column='Weight', default=0.0, max_digits=5, decimal_places=2)
    height = models.DecimalField(db_column='Height', default=0.0, max_digits=5, decimal_places=2)
    
    allergies = models.TextField(db_column='Allergies', blank=True, null=True)
    occupation = models.CharField(db_column='Occupation', max_length=50, blank=True, null=True)
    medication = models.TextField(db_column='Medication',  blank=True, null=True)
    supplements = models.TextField(db_column='Supplements', blank=True, null=True)
    surgery = models.TextField(db_column='Surgery', max_length=100, blank=True, null=True)
    past_illnesses = models.TextField(db_column='PastIllnesses', max_length=100, blank=True, null=True)
    family_history = models.TextField(db_column='FamilyHistory', max_length=100, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'PatientDetails'
    
    """
    refer back to parent 'patient' record to get name details etc.
    In one to one relationship, use patient one to one declaration above to access feilds
    """
    def __str__(self):
        return '%s %s' % (self.patient.first_name, self.patient.last_name)


class PatientConsult(TimeStampedModel):
    summary = models.CharField(db_column='Summary', max_length=100)
    details = models.TextField(db_column='Details', blank=True, null=True)
    presenting_symptoms = models.TextField(db_column='PresentingSymptoms', blank=True, null=True)
    presenting_signs = models.TextField(db_column='PresentingSigns', blank=True, null=True)
    """
    Each consult record needs the key of the patient it is associated with
    """
    patient_consult = models.ForeignKey(Patient, verbose_name="Patient", on_delete=models.CASCADE, related_name='consultdetails')

    class Meta:
        managed = True
        db_table = 'PatientConsults'

    """
    refer back to parent 'patient' record to get name details etc.
    In foreign key one to many, use patient_consult foreign key declaration as above
    declaration above to access fields
    """
    def __str__(self):
        return '%s %s' % (self.patient_consult.first_name, self.patient_consult.last_name)


class HealthFund(TimeStampedModel):
    fund_name = models.CharField(db_column='Name', max_length=100)
    provider_no = models.CharField(db_column='Provider', max_length=100, blank=True, null=True)
    
    class Meta:
        managed = True
        db_table = 'HealthFunds'
        ordering = ['fund_name']

    def __str__(self):
        return self.fund_name


class HerbIndication(TimeStampedModel):
    """
    Define the herbal medicine indications table - inherits two timestamp fields from abstract class TimeStampedModel
    """
    herbindication_id = models.AutoField(db_column='HerbIndicationId', primary_key=True)  
    herbindication_name = models.CharField(db_column='HerbIndicationName', max_length=50, verbose_name="Herb Indication",
        unique=True) 

    herbmed_indications = models.ManyToManyField('HerbalMedicine', verbose_name='Related Herbal Medicines')

    class Meta:
        managed = True
        db_table = 'HerbIndications'
        ordering = ['herbindication_name']
    
    def __str__(self):
        return self.herbindication_name


class HerbAction(TimeStampedModel):
    """
    Define the herbal medicine actions table - inherits two timestamp fields from abstract class TimeStampedModel
    """
    herbaction_id = models.AutoField(db_column='HerbActionId', primary_key=True)  
    herbaction_name = models.CharField(db_column='HerbActionName', max_length=50, verbose_name="Herb Action", unique=True) 

    herbmed_actions = models.ManyToManyField('HerbalMedicine', verbose_name='Related Herbal Medicines')

    class Meta:
        managed = True
        db_table = 'HerbActions'
        ordering = ['herbaction_name']    
    
    def __str__(self):
        return self.herbaction_name


class ProductStrength(TimeStampedModel):
    strength = models.CharField(db_column='Strength', max_length=4)
    notes = models.CharField(db_column='Notes', max_length=50, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'ProductStrengths'
        ordering = ['strength']
    
    def __str__(self):
        return self.strength


class Product(TimeStampedModel):
    """
    Define the herbal medicine product details table - inherits two timestamp fields from abstract class TimeStampedModel
    """
    ''' STRENGTH_CHOICES = (('1:1', '1:1'), ('1:2','1:2'), ('1:3', '1:3'), ('1:5', '1:5'), ('1:10', '1:10'), ('2:1', '2:1'), 
                         ('NA', 'NA')) '''
    UNITSIZE_CHOICES = (('L', 'Litres'), ('MLS', 'Mls'))

    product_id = models.AutoField(db_column='ProductId', primary_key=True)  
    product_name = models.CharField(db_column='ProductName', max_length=50)
    product_code = models.CharField(db_column='ProductCode', max_length=20, blank=True, null=True)
    #product_strength = models.CharField(db_column='ProductStrength', max_length=20, choices=STRENGTH_CHOICES, default='1:2')
    product_qty = models.DecimalField(db_column='ProductQty', max_digits=6, decimal_places=2)
    product_unit = models.CharField(db_column='ProductUnitSize', max_length=10, choices=UNITSIZE_CHOICES, default='MLS')
    product_cost = models.DecimalField(db_column='ProductCost', max_digits=6, decimal_places=2)
    product_dose = models.CharField(db_column='ProductDose', max_length=50, blank=True, null=True)
    
    product_brand = models.ForeignKey('Brand', verbose_name="Related brand", on_delete=models.CASCADE, related_name="productbrand")
    product_strength = models.ForeignKey('ProductStrength', on_delete=models.CASCADE)

    herbmed_product = models.ManyToManyField('HerbalMedicine', blank=True, verbose_name="Related herbal medicines")
    
    class Meta:
        managed = True
        db_table = 'Products'
        ordering = ['product_name']
    
    """
    format product name returned for display in formula list etc.
    """
    def __str__(self):
        return "%s %s %s" % (self.product_brand.brand_short, self.product_name, self.product_strength.strength)



class HerbalMedicine(TimeStampedModel):
    """
    Define the herbal medicine details table - inherits two timestamp fields from abstract class TimeStampedModel
    """
    herb_id = models.AutoField(db_column='HerbId', primary_key=True)  
    herb_name = models.CharField(db_column='HerbName', max_length=50) 
    herb_botanical_name = models.CharField(db_column='HerbBotanical', max_length=255, blank=True, null=True) 
    herb_description = models.CharField(db_column='HerbDescription', max_length=255, blank=True, null=True)
    herb_parts_used = models.CharField(db_column='HerbPartsUsed', max_length=255, blank=True, null=True)
    #   allows for reverse m2m with HerbIndication - 1/5/2019 - data is stored in the HerbIndication_herbmed_indications table
    #      this is only a pass through no data stored here
    indications_herbmed = models.ManyToManyField('HerbIndication', through=HerbIndication.herbmed_indications.through,
        verbose_name='Related Indications', blank=True)
    #   allows for reverse m2m with HerbAction - 1/5/2019 - data is stored in the Herbaction_herbmed_actions table
    #      this is only a pass through no data stored here
    actions_herbmed = models.ManyToManyField('HerbAction', through=HerbAction.herbmed_actions.through,
        verbose_name='Related Actions', blank=True)
    #   allows for reverse m2m with Product - 1/5/2019 - data is stored in the Products_herbmed_product table
    #      this is only a pass through no data stored here
    products_herbmed = models.ManyToManyField('Product', through=Product.herbmed_product.through,
        verbose_name='Related Products', blank=True)

    class Meta:
        managed = True
        db_table = 'HerbalMedicines'
        ordering = ['herb_name']
    
    
    def __str__(self):
        return self.herb_name


class Brand(TimeStampedModel):
    brand_id = models.AutoField(db_column='BrandId', primary_key=True)  
    brand_name = models.CharField(db_column='BrandName', max_length=50, unique=True)
    brand_short = models.CharField(db_column='BrandAbbrev', max_length=5, blank=True, null=True)

    supplier_brand = models.ManyToManyField('Supplier', verbose_name='Related Supplier', related_name='supplierbrand')
    
    class Meta:
        managed = True
        db_table = 'Brands'
        ordering = ['brand_name']
    
    def __str__(self):
        return self.brand_name


class Supplier(TimeStampedModel):
    """
    Define the herbal medicine supplier details table - inherits two timestamp fields from abstract class TimeStampedModel
    """
    supplier_id = models.AutoField(db_column='SupplierId', primary_key=True)  
    supplier_name = models.CharField(db_column='SupplierName', max_length=50, unique=True)
    supplier_customer_code = models.CharField(db_column='SupplierCustCode', max_length=12, blank=True, null=True)
    address_1 = models.CharField(db_column='Address1', max_length=50, blank=True, null=True) 
    address_2 = models.CharField(db_column='Address2', max_length=50, blank=True, null=True)
    city = models.CharField(db_column='City', max_length=20, blank=True, null=True)
    state = models.CharField(db_column='State', max_length=3, choices=STATE_CHOICES, default='NSW') 
    postcode = models.CharField(db_column='PostCode', max_length=4, blank=True, null=True)
    phone = models.CharField(db_column='Phone', max_length=10, blank=True, null=True)
    email = models.EmailField(db_column='Email', max_length=50, blank=True, null=True)
    mobile = models.CharField(db_column='Mobile', max_length=10, blank=True, null=True)
    supplier_rep = models.CharField(db_column='SupplierRep', max_length=50, blank=True, null=True)

    #   allows for reverse m2m with HerbAction - 1/5/2019 - data is stored in the Herbaction_herbmed_actions table
    #      this is only a pass through no data stored here
    brand_supplier = models.ManyToManyField(Brand, through=Brand.supplier_brand.through,
        verbose_name='Related Products', blank=True)

    class Meta:
        managed = True
        db_table = 'Suppliers'
        ordering = ['supplier_name']
    
    def __str__(self):
        return self.supplier_name


class FormulaBottleSize(TimeStampedModel):
    UNITSIZE_CHOICES = (('L', 'Litres'), ('MLS', 'Mls'))
    
    bottle_size = models.IntegerField()
    bottle_notes = models.CharField(db_column='Notes', max_length=50, blank=True, null=True)
    bottle_unit = models.CharField(db_column='BottleUnitSize', max_length=10, choices=UNITSIZE_CHOICES, default='MLS')

    class Meta:
        managed = True
        db_table = 'FormulaBottleSizes'
        ordering = ['bottle_size']

    def __str__(self):
        return "%s %s %s" % (self.bottle_size, self.bottle_unit, self.bottle_notes)


class FormulaSetting(TimeStampedModel):
    formula_settings_id = models.AutoField(primary_key=True)
    formula_bottle_size = models.ForeignKey('FormulaBottleSize', on_delete=models.CASCADE)
    formula_bottle_cost = models.DecimalField(max_digits=5, decimal_places=2, default=2.00)
    formula_bottle_size_mu = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    formula_bottle_size_min_rrp = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    formula_dispensing_fee = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    class Meta:
        managed = True
        db_table = 'FormulaSettings'
        ordering = ['formula_bottle_size']
    
    def __str__(self):
        return str(self.formula_bottle_size)


class HerbalFormula(TimeStampedModel):

    FORMULATYPES = (
        ('T', 'Total mls per herb'),
        ('M', 'Mls per dose'),
        ('D', 'Drops per dose'),
        ('P', 'Percentage per bottle'),
    )

    """
    Define the herbal formula table - inherits two timestamp fields from abstract class TimeStampModel
    """
    formula_id = models.AutoField(db_column='FormulaId', primary_key=True)
    formula_code = models.CharField(db_column='FormulaCode', max_length=50, unique=True)
    formula_type = models.CharField(db_column='FormulaType', max_length=1, choices=FORMULATYPES, default="M")
    """
    Many to many relationship between patients and formulas
    Specify the model that will be used to govern the many to many relationship
    which is DispensedItem, then we can add extra fields to that model
    """
    patient_formulas = models.ManyToManyField(Patient, through='DispensedItem')
    formula_ingredients = models.ManyToManyField(Product, through='FormulaHerbItem', related_name='itemquantity')

    class Meta:
        managed = True
        db_table = 'HerbalFormulas'
        ordering = ['formula_code']
    
    def __str__(self):
        return self.formula_code


class DispensedItem(TimeStampedModel):

    MEASURES = (
        ('mls', 'mls'),
        ('drops', 'drops'),
    )

    QTYTYPE = (
        ('mls', 'mls'),
        ('litre', 'litre'),
    )

    SIZES = ((1,1), (2,2), (15,15), (25,25), (50,50), (100,100), (200,200), (500,500))
    """
    Add details of the dispensed herbal formula 
    """
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='patientf')
    formula = models.ForeignKey(HerbalFormula, on_delete=models.CASCADE, related_name='formulap')
    """
    Now define other fields that we need also - date dispensed will be auto from TimeStamp Model
    """
    # dispensed item specific information
    quantity = models.IntegerField(choices=SIZES, default=200)
    qtytype = models.CharField(choices=QTYTYPE, default="mls", max_length=5)
    doseage = models.DecimalField(max_digits=4, decimal_places=2)
    measure = models.CharField(choices=MEASURES, default="mls", max_length=5)
    frequency = models.CharField(max_length=30, default="3 x daily")
    administerin = models.CharField(max_length=30, default="in water or juice")
    directions = models.CharField(max_length=30, default="with food")

    class Meta:
        managed = True
        db_table = 'DispensedItems'
    
    def __str__(self):
        return self.formula.formula_code
    

class FormulaHerbItem(TimeStampedModel):
    """
    Add details of the intermediary table holding references to dispensed herbs in a formula
    by formula and product 
    """
    formula = models.ForeignKey(HerbalFormula, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    """
    Now define other fields that we need also - date dispensed will be auto from TimeStamp Model
    """
    # quantity of herb in the formula
    quantity = models.DecimalField(max_digits=4, decimal_places=2)

    class Meta:
        managed = True
        db_table = 'FormulaHerbItems'
    
    def __str__(self):
        return self.product.product_name