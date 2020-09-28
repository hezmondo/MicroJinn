INSERT INTO mjinn.rental_trans 
SELECT 0, Date, Amount, Payee, Memo,
CASE
	WHEN Memo LIKE "%OLHR137 rental income%" THEN 1 
	WHEN Memo LIKE "%BUST1 rental income%" THEN 2 
	WHEN Memo LIKE "%BUST3 rental income%" THEN 3 
	WHEN Memo LIKE "%BUST11 rental income%" THEN 4
	WHEN Memo LIKE "%BUST13 rental income%" THEN 5
	WHEN Memo LIKE "%BARF50 rental income%" THEN 6
	WHEN Memo LIKE "%BARF52 rental income%" THEN 7
	WHEN Memo LIKE "%SHWR101 rental income%" THEN 8
	WHEN Memo LIKE "%SHWR103 rental income%" THEN 9
END
FROM yoda.bank_transaction
WHERE ID > 34265
AND Cat = 63
ORDER BY Date
;