#SELECT * FROM yoda.bank_transaction
SELECT SUM(Amount) FROM yoda.bank_transaction
#WHERE Date > "2020-06-01"
WHERE Account = 11
#WHERE Memo LIKE "%agepay%"
#WHERE Cat IN (46, 70)
#AND Cat != 34
#AND Date >= "2014-01-25"
AND Date > "2020-06-02"
ORDER BY Date
#AND Amount = 95
#ORDER BY Date DESC;