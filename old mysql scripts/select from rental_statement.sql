SET @tot := 0;

SELECT id, date, memo, amount, payer, (@tot := @tot + amount) as balance 
FROM mjinn.rental_statement
ORDER BY date, id
;