#SELECT 
UPDATE
#m.rentcode, m.tenantname, m.rentpa, m.arrears, m.lastrentdate, 
#y.TenantName, y.Rent, y.Arrears, y.LastRentDate
#FROM
mjinn.rent m
LEFT JOIN yoda.rents y 
ON m.rentcode = y.RentCode 
#SET m.tenantname = y.TenantName, m.rentpa = y.Rent, m.arrears = y.Arrears, m.lastrentdate = y.LastRentDate;
#SET mailto_id =
#CASE #
#	WHEN `MailTo` = 'A' THEN 1
#	WHEN `MailTo` = 'C' THEN 2
#	WHEN `MailTo` = 'N' THEN 3
#	WHEN `MailTo` = 'O' THEN 4
#END
SET prdelivery_id =
CASE
	WHEN `PrDelivery` = 'E' THEN 1
	WHEN `PrDelivery` = 'M' THEN 2
END
