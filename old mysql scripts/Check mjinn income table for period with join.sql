SELECT * FROM mjinn.income mi
#SELECT SUM(mi.total) FROM mjinn.income mi
LEFT JOIN mjinn.incomealloc ma
ON ma.income_id = mi.id
#WHERE payer LIKE "%McHale%"
WHERE mi.typebankacc_id = 14
AND mi.typepayment_id = 2
#AND total > 500
AND mi.paydate >= "2014-04-15"
#AND paydate > "2019-01-19"
#ORDER BY paydate;