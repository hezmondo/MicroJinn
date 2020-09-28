SELECT * FROM yoda.income i
LEFT JOIN yoda.income_allocation ia
ON ia.IncomeID = i.IncomeID
#WHERE payer LIKE "%McHale%"
WHERE i.BankType = 14
AND i.PaymentType = 2
#AND total > 500
AND i.paydate >= "2014-04-15"
#AND paydate > "2019-01-19"
#ORDER BY paydate;