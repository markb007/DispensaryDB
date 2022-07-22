select row_to_json(herbalformulas) as herbalformulas
from (
	select a."FormulaId", a."created", a."FormulaCode", a."FormulaType",
	(select json_agg(herbs)
		from 
	 		(select * from "FormulaHerbItems" FHI where a."FormulaId" = FHI."formula_id"
		) herbs
	) as FormulaHerbItems
from "HerbalFormulas" as a) herbalformulas