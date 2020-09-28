INSERT INTO mjinnx.property (id, propaddr, rent_id, typeprop_id)
SELECT 0, PropAddress, mr.id, 
    CASE
        WHEN `PropType` = 'C' THEN 1
        WHEN `PropType` = 'F' THEN 2
        WHEN `PropType` = 'G' THEN 3
        WHEN `PropType` = 'H' THEN 4
        WHEN `PropType` = 'L' THEN 5
        WHEN `PropType` = 'M' THEN 6
        ELSE 1
	END
FROM yoda.properties p LEFT JOIN yoda.rents r
ON p.RentCode = r.RentCode
LEFT JOIN mjinnx.rent mr
ON r.RentCode = mr.rentcode
WHERE r.RentCode LIKE "A%"
AND r.Status NOT IN ("S", "T")
AND r.RentCode NOT LIKE "ASR394%"
;