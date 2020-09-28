TRUNCATE mjinn.charge;
INSERT INTO mjinn.charge
SELECT 0, ChargeType, ChargeStartDate, ChargeTotal, ChargeDetails, ChargeBalance, r.id 
FROM yoda.charges c INNER JOIN mjinn.rent r 
ON c.RentCode = r.RentCode
;