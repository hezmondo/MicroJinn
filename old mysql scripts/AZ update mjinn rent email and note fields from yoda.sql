#SELECT r.rentcode, r.email, c.Email, c.Notes FROM
UPDATE 
mjinn.rent r
INNER JOIN yoda.contacts c
ON r.rentcode = c.RentCode
SET r.email = c.Email, r.note = c.Notes
#WHERE r.RentCode IN (SELECT c.RentCode from yoda.contacts)
