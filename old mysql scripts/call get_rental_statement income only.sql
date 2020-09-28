Use `mjinn`;

SET @thisrentalid = 7;

CALL pop_rental_statement(@thisrentalid);

SELECT date, DATE_FORMAT(date, '%d/%m/%Y') AS NiceDate, memo, amount, payer, balance 
FROM rental_statement
WHERE amount > 0
ORDER BY date;
