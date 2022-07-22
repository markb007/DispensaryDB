from csv import DictReader
from datetime import datetime

from django.core.management import BaseCommand
from django.conf import settings

from patientdb.models import Brand, Supplier, Product, ProductStrength, \
    HerbalMedicine, HealthFund, FormulaBottleSize, FormulaSetting
    
from pytz import UTC

class Command(BaseCommand):
    # Show this when the user types help
    help = """
    ##################################################### 
    Loads brand, supplier, herbal medicine, product data, 
    health fund, bottle sizes and settings from csv files 
    into the models 
    #####################################################"""

    def handle(self, *args, **options):
        ############################################
        print("Checking brands ...")
        ############################################
        if Brand.objects.exists():
            print("Brand data already exists ... bypassing brand import")
        else:
            for row in DictReader(open('./import_initial_data/Brand-2019.csv')):
                brand = Brand()
                brand.brand_name = row['brand_name']
                brand.brand_short = row['brand_short']
                brand.save()
            print("Brands loaded ...")
        
        ######################################
        print("Checking suppliers ...")
        ######################################
        if Supplier.objects.exists():
            print("Supplier data already exists ... bypassing supplier import")
        else:
            for row in DictReader(open('./import_initial_data/Supplier-2019.csv')):
                supplier = Supplier()
                supplier.supplier_name = row['supplier_name']
                supplier.supplier_customer_code = row['supplier_customer_code']
                supplier.address_1 = row['address_1']
                supplier.address_2 = row['address_2']
                supplier.city = row['city']
                supplier.state = row['state']
                supplier.postcode = row['postcode']
                supplier.email = row['email']
                supplier.phone = row['phone']
                supplier.mobile = row['mobile']
                supplier.supplier_rep = row['supplier_rep']
                # save before adding m2m
                supplier.save()

                supplierbrand_names = [name for name in row['brand_supplier'].split(',') if name]
                for supplierbrand_name in supplierbrand_names:
                    supbrand = 'something'
                    try:
                        supbrand = Brand.objects.get(brand_name=supplierbrand_name.strip())
                    except Brand.DoesNotExist:
                    # create brand if it does not exist
                        supbrand = Brand()
                        supbrand.brand_name = supplierbrand_name
                        supbrand.save()            
                    # m2m
                    supplier.brand_supplier.add(supbrand)
                
                supplier.save()
            
            print("Suppliers loaded ...")

        ######################################################
        print("Checking ProductStrengths ...")
        ######################################################
        if ProductStrength.objects.exists():
            print("ProductStrength data already exists ... bypassing import")
        else:
            for row in DictReader(open('./import_initial_data/Product_Strength-2019.csv')):
                strength = ProductStrength()
                strength.strength = row['strength']
                strength.notes = row['notes']
                strength.save()
            print("ProductStrengths loaded ...")

        
        ######################################################
        print("Checking Health Funds ...")
        ######################################################
        if HealthFund.objects.exists():
            print("HealthFund data already exists ... bypassing import")
        else:
            for row in DictReader(open('./import_initial_data/HealthFund-2019.csv')):
                fund = HealthFund()
                fund.fund_name = row['fund_name']
                fund.provider_no = row['provider_no']
                fund.save()
            print("HealthFunds loaded ...")

        
        ######################################################
        print("Checking Bottle Sizes ...")
        ######################################################
        if FormulaBottleSize.objects.exists():
            print("Bottle size data already exists ... bypassing import")
        else:
            for row in DictReader(open('./import_initial_data/FormulaBottleSize-2019.csv')):
                bottle = FormulaBottleSize()
                bottle.id = row['id']
                bottle.bottle_size = row['bottle_size']
                bottle.notes = row['bottle_notes']
                bottle.bottle_unit = row['bottle_unit']
                bottle.save()
            print("Bottle sizes loaded ...")

        ######################################################
        print("Checking Formula Settings ...")
        ######################################################
        if FormulaSetting.objects.exists():
            print("Formula Settings data already exists ... bypassing import")
        else:
            for row in DictReader(open('./import_initial_data/FormulaSetting-2019.csv')):
                setting = FormulaSetting()
                setting.formula_settings_id = row['formula_settings_id']
                setting.formula_bottle_size = FormulaBottleSize.objects.get(pk=row['formula_bottle_size'])
                setting.formula_bottle_cost = row['formula_bottle_cost']
                setting.formula_bottle_size_mu = row['formula_bottle_size_mu']
                setting.formula_bottle_size_min_rrp = row['formula_bottle_size_min_rrp']
                setting.formula_dispensing_fee = row['formula_dispensing_fee']
                setting.save()
            print("Bottle sizes loaded ...")

        #############################################
        print("Checking herbal medicines ...")
        #############################################
        if HerbalMedicine.objects.exists():
            print("HerbalMedicine data already exists ... bypassing import")
        else:
            for row in DictReader(open('./import_initial_data/HerbalMedicine-2019.csv')):
                herbalmedicine = HerbalMedicine()
                herbalmedicine.herb_name = row['herb_name']
                herbalmedicine.herb_botanical_name = row['herb_botanical_name']
                herbalmedicine.herb_description = row['herb_description']
                herbalmedicine.herb_description = row['herb_parts_used']
                herbalmedicine.save()
            print("HerbalMedicines loaded .....")

        ######################################    
        print("Loading product data ")
        ######################################
        index = 0
        for row in DictReader(open('./import_initial_data/Mediherb_product_list.csv')):
            index += 1
            if index == 1:
                if Product.objects.filter(product_brand__brand_name=row['product_brand']):
                    print("Products already exist for brand .... bypassing import")
                    break

            product = Product()
            product.product_code = row['product_code']
            product.product_name = row['product_name']
            product.product_qty = row['product_qty']
            product.product_unit = row['product_unit']
            product.product_cost = row['product_cost']
            
            product.product_brand = Brand.objects.get(brand_name=row['product_brand'])
            product.product_strength = ProductStrength.objects.get(strength=row['product_strength'])
            # get product_id prior to m2m
            product.save()

            herbmed_names = [name for name in row['herbmed_product'].split(',') if name]
            for herbmed_name in herbmed_names:
                herbmed = 'something'
                try:
                    herbmed = HerbalMedicine.objects.get(herb_name=herbmed_name.strip())
                except HerbalMedicine.DoesNotExist:
                # create herbal medicine if it does not exist
                    herbmed = HerbalMedicine()
                    herbmed.herb_name = herbmed_name
                    herbmed.save()            
                # m2m
                product.herbmed_product.add(herbmed)
            
            product.save()