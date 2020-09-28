UPDATE mjinn.rent r LEFT JOIN mjinn.incomealloc ia
ON r.rentcode = ia.rentcode
SET ia.rent_id = r.id;