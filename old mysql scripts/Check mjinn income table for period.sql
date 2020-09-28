SELECT * FROM mjinn.income
#SELECT SUM(total) FROM mjinn.income
#WHERE payer LIKE "%McHale%"
#WHERE typebankacc_id = 11
#AND typepayment_id = 2
#AND total = 125
WHERE paydate >= "2020-05-25"
#AND paydate > "2019-01-19"
ORDER BY paydate;