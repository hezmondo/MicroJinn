Use `samjinn`;

SET @thisloanid = 1;

CALL pop_loan_statement(@thisloanid);

SELECT DATE_FORMAT(date, '%d/%m/%Y') AS Date, memo, transaction, interest, rate, add_interest, balance FROM loan_statement;
