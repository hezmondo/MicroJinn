INSERT INTO mjinn.rent (id, rentcode, tenantname, rentpa, arrears, lastrentdate, datecode, source, price, email, note, landlord_id, 
agent_id, actype_id, advarr_id, deed_id, freq_id, mailto_id, prdelivery_id, salegrade_id, status_id, tenure_id)
SELECT 0, RentCode, TenantName, Rent, Arrears, LastRentDate, DateCode, Source, 99999, "", "",
    CASE Landlord
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
    1,
    CASE
        WHEN `AcType` = 'A' THEN 1
        WHEN `AcType` = 'N' THEN 2
        WHEN `AcType` = 'P' THEN 3
        WHEN `AcType` = 'R' THEN 4
        WHEN `AcType` = 'S' THEN 5
	END,
    CASE
        WHEN `AdvArr` = 'R' THEN 1
        ELSE 2
	END,
16,     
Frequency,
	CASE
        WHEN `MailTo` = 'A' THEN 1
        WHEN `MailTo` = 'C' THEN 2
        WHEN `MailTo` = 'N' THEN 3
        WHEN `MailTo` = 'O' THEN 4
	END,
    CASE
        WHEN `PrDelivery` = 'E' THEN 1
        WHEN `PrDelivery` = 'M' THEN 2
	END,
    TitleGrade,
    CASE
        WHEN `Status` = 'A' THEN 1
        WHEN `Status` = 'C' THEN 2
        WHEN `Status` = 'G' THEN 3
        WHEN `Status` = 'N' THEN 4
        WHEN `Status` = 'S' THEN 5
        WHEN `Status` = 'T' THEN 6
        WHEN `Status` = 'X' THEN 7
	END,
    CASE
        WHEN `Tenure` = 'F' THEN 1
        WHEN `Tenure` = 'L' THEN 2
        WHEN `Tenure` = 'R' THEN 3
	END
FROM yoda.rents
WHERE RentCode LIKE "ZVIC%"
;