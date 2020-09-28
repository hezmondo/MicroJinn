INSERT into mjinn.money_item
SELECT 0, Num, Date, Payee, Amount, Memo, Cat,
CASE 
	WHEN Recon = "C" THEN 0
    ELSE 1
END,
Account
FROM yoda.bank_transaction
WHERE ID > 35111
AND Cat != 34
