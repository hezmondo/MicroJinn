INSERT INTO mjinn.headrent (id, hrcode, propaddr, rentpa, arrears, lastrentdate, datecode, source, reference, note, landlord_id, agent_id, advarr_id, freq_id, status_id, tenure_id)
SELECT 0, HRCode, PropAddr, Rent, Arrears, LastRentDate, DateCode, Source, Ref, Note,
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
END, 1,
CASE
	WHEN AdvArr = 'R' THEN 1
	ELSE 2
END, Frequency,
CASE
	WHEN Status = 'A' THEN 1
	WHEN AdvArr = 'D' THEN 2
	ELSE 3
END,
CASE
	WHEN Tenure = 'F' THEN 1
	WHEN Tenure = 'L' THEN 2
	ELSE 3
END
FROM yoda.headrents 