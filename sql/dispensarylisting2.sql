SELECT distinct on (D.id) D.*, H."FormulaCode", array_agg(FHI."quantity") as quantities, array_agg(PR."ProductName") as products, 
		array_agg(PR."product_brand_id") as brands, array_agg(PR."product_strength_id") as productstrength,
		array_agg(B."BrandAbbrev") as brandabbrev, array_agg(PS."Strength") as strength, 
		array_agg(distinct concat(P."FirstName", ' ', P."LastName")) as patientname
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
where D.created::date between date '2018-10-16' and current_date
group by d.id, H."FormulaCode"