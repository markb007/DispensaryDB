SELECT D.*, H."FormulaCode", H."FormulaType", FHI."quantity", P."FirstName", P."LastName", PR."ProductName", B."BrandAbbrev", PS."Strength"
FROM public."DispensedItems" D
/* everything from dispenseditems */
left join "HerbalFormulas" H on D."formula_id" = H."FormulaId"
/* get formula herb items for each formula */
inner join "FormulaHerbItems" FHI on H."FormulaId" = FHI."formula_id"
/* and the product names */
inner join "Products" PR on PR."ProductId" = FHI.product_id
/* and the brand of the product */
inner join "Brands" B on PR.product_brand_id = B."BrandId"
inner join "ProductStrengths" PS on PS."id" = PR.product_strength_id
/* and the patient it was allocated to */
inner join "Patients" P on P."PatientId" = D.patient_id
where D.created::date between date '2019-10-16' and current_date