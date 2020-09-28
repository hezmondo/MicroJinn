SELECT SUM(amount) FROM mjinn.money_transaction
#SELECT * FROM mjinn.money_transaction
#WHERE amount = 1500
WHERE acc_id = 11
AND date >= "2014-01-25"
#AND cleared = 1
#AND amount < 0
#AND date >= "2015-01-01"
#ORDER BY date DESC
;