	USE `mjinn`;

SELECT id, code, val_date, valuation, interest_pa, lender, borrower FROM loan
UNION
SELECT NULL, "Totals", "", SUM(valuation), SUM(interest_pa), "", ""  FROM loan
;
