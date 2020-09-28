UPDATE
mjinn.rent m
LEFT JOIN yoda.rents y 
ON m.rentcode = y.RentCode 
LEFT JOIN yoda.contacts c
ON m.rentcode = c.RentCode 

SET m.tenantname = y.TenantName, m.rentpa = y.Rent, m.arrears = y.Arrears, 
m.lastrentdate = y.LastRentDate, m.datecode = y.DateCode, m.source = y.Source,
m.price = y.Price, m.email = c.Email, m.note = c.Notes, 
landlord_id =
CASE
	WHEN Landlord = 1 THEN 1
	WHEN Landlord = 2 THEN 2
	WHEN Landlord = 3 THEN 3
	WHEN Landlord = 5 THEN 5
	WHEN Landlord = 8 THEN 8
	WHEN Landlord = 9 THEN 9
	WHEN Landlord = 13 THEN 7
	WHEN Landlord = 18 THEN 4
	WHEN Landlord = 20 THEN 6
ELSE 10
END,
#agent
actype =
CASE
	WHEN `AcType` = 'A' THEN 1
	WHEN `AcType` = 'N' THEN 2
	WHEN `AcType` = 'P' THEN 3
	WHEN `AcType` = 'R' THEN 4
	WHEN `AcType` = 'S' THEN 5
END,
advarr =
CASE
	WHEN `AdvArr` = 'R' THEN 1
	ELSE 2
END,
#deed_id
m.freq_id = y.Frequency,
mailto_id =
CASE
	WHEN `MailTo` = 'A' THEN 1
	WHEN `MailTo` = 'C' THEN 2
	WHEN `MailTo` = 'N' THEN 3
	WHEN `MailTo` = 'O' THEN 4
END,
prdelivery_id =
CASE
	WHEN `PrDelivery` = 'E' THEN 1
	WHEN `PrDelivery` = 'M' THEN 2
END,
m.salegrade_id = y.TitleGrade,
status_id =
CASE
	WHEN `Status` = 'A' THEN 1
	WHEN `Status` = 'C' THEN 2
	WHEN `Status` = 'G' THEN 3
	WHEN `Status` = 'N' THEN 4
	WHEN `Status` = 'S' THEN 5
	WHEN `Status` = 'T' THEN 6
	WHEN `Status` = 'X' THEN 7
END,
tenure_id =
CASE
	WHEN `Tenure` = 'F' THEN 1
	WHEN `Tenure` = 'L' THEN 2
	WHEN `Tenure` = 'R' THEN 3
END
WHERE m.rentcode LIKE "ZCAB%"
;