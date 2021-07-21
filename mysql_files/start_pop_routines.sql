USE mjinn;

DELIMITER ;;
CREATE FUNCTION `acc_balance`(id integer, cvalue integer, todate date) RETURNS decimal(10,2)
    DETERMINISTIC
BEGIN
	DECLARE transtotal decimal(10,2);
	DECLARE bacstotal decimal(10,2);
    SELECT SUM(amount) FROM money_item WHERE acc_id = id AND date <= todate AND cleared = cvalue INTO transtotal;
    SELECT SUM(amount) FROM income  WHERE acc_id = id AND date <= todate AND paytype_id NOT IN (1, 6) INTO bacstotal;
    IF cvalue = 1 THEN
		RETURN IFNULL(transtotal, 0) + IFNULL(bacstotal, 0);
	ELSE
		RETURN IFNULL(transtotal, 0);
	END IF;
END ;;
DELIMITER ;

DELIMITER ;;
CREATE FUNCTION `acc_total`(cvalue integer) RETURNS decimal(10,2)
    DETERMINISTIC
BEGIN
	DECLARE transtotal decimal(10,2);
	DECLARE bacstotal decimal(10,2);
    SELECT SUM(amount) FROM money_item WHERE cleared = cvalue INTO transtotal;
	IF cvalue = 0 THEN
		RETURN IFNULL(transtotal, 0);
	ELSE
		SELECT SUM(amount) FROM income  WHERE paytype_id = 2 INTO bacstotal;
		RETURN IFNULL(transtotal, 0) + IFNULL(bacstotal, 0);
	END IF;
END ;;
DELIMITER ;

DELIMITER ;;
CREATE FUNCTION `calc_int`(
intrate decimal(8,2), balance decimal(8,2), enddate date, startdate date
) RETURNS decimal(8,2)
    DETERMINISTIC
BEGIN
	RETURN DATEDIFF(enddate, startdate)*balance*intrate/36525;
END ;;
DELIMITER ;

DELIMITER ;;
CREATE FUNCTION `last_arrears_level`(rentid int) RETURNS char(1) CHARSET utf8mb4
    DETERMINISTIC
BEGIN

RETURN (SELECT arrears_level FROM pr_history 
WHERE id = (SELECT MAX(id) FROM pr_history WHERE rent_id = rentid AND delivery_method NOT IN (4,5,6)))
;
END ;;
DELIMITER ;

DELIMITER ;;
CREATE FUNCTION `last_payment`(rentid int) RETURNS decimal(10,2)
    DETERMINISTIC
BEGIN

RETURN (SELECT i.amount FROM income i RIGHT JOIN incomealloc ia 
ON ia.income_id = i.id WHERE ia.rent_id = rentid
ORDER BY i.date DESC
LIMIT 1);
END ;;
DELIMITER ;

DELIMITER ;;
CREATE FUNCTION `last_payment_date`(rentid int) RETURNS date
    DETERMINISTIC
BEGIN

RETURN (SELECT i.date FROM income i RIGHT JOIN incomealloc ia 
ON ia.income_id = i.id WHERE ia.rent_id = rentid
ORDER BY i.date DESC
LIMIT 1);
END ;;
DELIMITER ;

DELIMITER ;;
CREATE FUNCTION `last_recovery_level`(rentid int) RETURNS char(1) CHARSET utf8mb4
    DETERMINISTIC
BEGIN

RETURN (SELECT arrears_level FROM pr_history 
WHERE id = (SELECT MAX(id) FROM pr_history WHERE rent_id = rentid AND delivery_status != 'T'))
;
END ;;
DELIMITER ;

DELIMITER ;;
CREATE FUNCTION `newest_charge`(rentid int) RETURNS date
    DETERMINISTIC
BEGIN

RETURN (SELECT MAX(chargestartdate) FROM charge 
WHERE rent_id = rentid)
;
END ;;
DELIMITER ;

DELIMITER ;;
CREATE FUNCTION `next_date`(start_date date, frequency  int, periods int) RETURNS date
    DETERMINISTIC
BEGIN
	DECLARE CUSTOM_EXCEPTION CONDITION FOR SQLSTATE '45000';
	-- this fn calculates a new date exactly n periods forwards or backwards 
	CASE frequency
        WHEN 1 THEN
			RETURN DATE_ADD(start_date, INTERVAL 1*periods YEAR);
        WHEN 2 THEN
			RETURN DATE_ADD(start_date, INTERVAL 6*periods MONTH);
        WHEN 4 THEN
			RETURN DATE_ADD(start_date, INTERVAL 3*periods MONTH);
        WHEN 12 THEN
			RETURN DATE_ADD(start_date, INTERVAL 1*periods MONTH);
        WHEN 13 THEN
			RETURN DATE_ADD(start_date, INTERVAL 4*periods WEEK);
        WHEN 52 THEN
			RETURN DATE_ADD(start_date, INTERVAL 1*periods WEEK);
	END CASE;

    SIGNAL CUSTOM_EXCEPTION
        SET MESSAGE_TEXT = 'Bad Frequency';

    RETURN NULL; 
END ;;
DELIMITER ;

DELIMITER ;;
CREATE DEFINER=`root`@`localhost` FUNCTION `next_rent_date`(rentid int, rentype int) RETURNS date
    DETERMINISTIC
BEGIN
	DECLARE startdate DATE;
    DECLARE frequency, dayval, datecodeid int;
	DECLARE CUSTOM_EXCEPTION CONDITION FOR SQLSTATE '45000';

    -- first we get the relevant data from either the rent table (if rentype = 1) or otherwise the headrent table
    IF rentype = 1 THEN
		SELECT lastrentdate, freq_id, datecode_id FROM rent WHERE id = rentid INTO startdate, frequency, datecodeid;
    ELSE
		SELECT lastrentdate, freq_id, datecode_id FROM headrent WHERE id = rentid INTO startdate, frequency, datecodeid;
	END IF;
    -- now we get a new pure date calculated forward 1 period
	CASE frequency
        WHEN 1 THEN
			SET startdate = DATE_ADD(startdate, INTERVAL 1 YEAR);
        WHEN 2 THEN
			SET startdate = DATE_ADD(startdate, INTERVAL 6 MONTH);
        WHEN 4 THEN
			SET startdate = DATE_ADD(startdate, INTERVAL 3 MONTH);
        WHEN 12 THEN
			SET startdate = DATE_ADD(startdate, INTERVAL 1 MONTH);
        WHEN 13 THEN
			SET startdate = DATE_ADD(startdate, INTERVAL 4 WEEK);
        WHEN 52 THEN
			SET startdate = DATE_ADD(startdate, INTERVAL 1 WEEK);
	END CASE;
    -- now we check, for frequencies 2 and 4 only, in case the new month and datecode_id appears in the
    -- special date_m table, in which case we enforce the day number for this special month/datecode_id pair
    IF frequency = 2 OR frequency = 4 THEN
		SELECT day FROM date_m WHERE code_id = datecodeid AND month = month(startdate) INTO dayval;
        IF dayval IS NOT NULL AND dayval > 0 THEN
			SET dayval = dayval - day(startdate);
			SET startdate = DATE_ADD(startdate, INTERVAL dayval DAY);
		END IF;
	END IF;
	RETURN startdate;

	SIGNAL CUSTOM_EXCEPTION
	SET MESSAGE_TEXT = 'Bad date data';
    RETURN NULL; 
END ;;
DELIMITER ;

DELIMITER ;;
CREATE DEFINER=`root`@`localhost` FUNCTION `total_owing`(rentid int) RETURNS decimal(8,2)
    DETERMINISTIC
BEGIN
	DECLARE r_arrears, total_charges decimal(8,2);

	SELECT arrears
	FROM rent WHERE id = rentid
	INTO r_arrears;

	SELECT IFNULL(SUM(chargebalance), 0)
	FROM charge WHERE rent_id = rentid
	INTO total_charges;

	RETURN (IFNULL(r_arrears, 0) + total_charges);
END ;;
DELIMITER ;

DELIMITER ;;
CREATE PROCEDURE `getincomeobj_yoda`(
IN start_id integer)
BEGIN
	DECLARE max_id INT;
    SELECT MAX(IncomeID) FROM yoda.income
    INTO max_id;
	WHILE start_id <= max_id DO
		INSERT INTO mjinn.income (id, date, payer, amount, paytype_id, acc_id)
		SELECT 0, PayDate, Payer, IncomeTotal, PaymentType, 
        CASE
			WHEN BankType = 23 THEN 13 
        ELSE BankType
        END
		FROM yoda.income
		WHERE IncomeID = start_id;
		INSERT INTO mjinn.incomealloc (id, rentcode, amount, chargetype_id, income_id, landlord_id, rent_id)
		SELECT 0, RentCode, AllocationTotal, ChargeType, LAST_INSERT_ID(),
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
		END, 1611
		FROM yoda.income_allocation
		WHERE IncomeID = start_id;
	  SET start_id = start_id + 1;
	END WHILE;
END ;;
DELIMITER ;

DELIMITER ;;
CREATE PROCEDURE `get_lt_trans`(
 in loanid INT
)
BEGIN
  DECLARE done BOOLEAN DEFAULT FALSE;
  DECLARE lt_id INT;
  DECLARE lt_date DATE;
  DECLARE lt_amount DECIMAL(8,2);
  DECLARE lt_memo VARCHAR(60);
  DECLARE cur CURSOR FOR SELECT id, date, amount, memo FROM loan_trans WHERE loan_id = loanid;
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET done := TRUE;

  OPEN cur;

  testLoop: LOOP
    FETCH cur INTO lt_id, lt_date, lt_amount, lt_memo;
    IF done THEN
      LEAVE testLoop;
    END IF;
  
	INSERT into loan_prep
	SELECT 0, lt_id, lt_date, lt_memo, lt_amount, 0, 0, 0;

  END LOOP testLoop;

  CLOSE cur;
END ;;
DELIMITER ;

DELIMITER ;;
CREATE PROCEDURE `get_period_vals`(
 in loanid INT, today_date date
)
BEGIN
  DECLARE freq, periods INT;
  DECLARE startdate DATE;
  DECLARE var_amount DECIMAL(8,2);
  DECLARE var_memo, freq_det VARCHAR(60);

  SELECT freq_id FROM loan
  WHERE id = loanid
  INTO freq;

  SELECT MIN(date) FROM loan_trans
  WHERE loan_id = loanid
  INTO startdate;

  SELECT freqdet FROM typefreq
  WHERE id = freq
  INTO freq_det;

  SET periods = 1;
  SET var_memo = CONCAT("interest added ", freq_det);

  WHILE next_date(startdate, freq, periods) < today_date DO
	INSERT into loan_prep
	SELECT 0, 0, next_date(startdate, freq, periods), var_memo, 0, 0, 1, 0;
    SET periods = periods + 1;
  END WHILE;
END ;;
DELIMITER ;

DELIMITER ;;
CREATE PROCEDURE `get_uplifts`(
 in loanid INT, today_date date
)
BEGIN
  DECLARE num INT;
  DECLARE startdate, vardate DATE;
  DECLARE int_rate DECIMAL(8,2);
  DECLARE var_memo VARCHAR(60);

  SELECT COUNT(*) 
  FROM loan_uplift
  WHERE loan_id = loanid
  AND datestarts < today_date
  INTO num ;

  SET vardate = "1990-01-01";
  
  WHILE num > 0 DO

    SELECT rate, start_date FROM loan_uplift
    WHERE loan_id = loanid
    AND start_date > vardate 
    ORDER BY start_date
    LIMIT 1
    INTO int_rate, startdate;

    SET var_memo = CONCAT("change interest rate to ", int_rate);

	INSERT into loan_prep
	SELECT 0, 0, startdate, var_memo, 0, int_rate, 0, 0;
    
    SET vardate = startdate;
    SET num = num - 1;

  END WHILE;
END ;;
DELIMITER ;

DELIMITER ;;
CREATE PROCEDURE `pop_mail_object`(IN rentid INT)
BEGIN
	SELECT 0, i.date, i.payer, i.amount, i.paytype_id FROM income i RIGHT JOIN incomealloc ia 
	ON ia.income_id = i.id WHERE ia.rent_id = rentid
	ORDER BY i.date DESC
	LIMIT 1;
END ;;
DELIMITER ;

DELIMITER ;;
CREATE PROCEDURE `pop_rental_statement`(
 in rentalid INT, calc_date date
)
BEGIN
  DECLARE freq INT;
  DECLARE start_rent_date, vardate DATE;
  DECLARE rent DECIMAL(8,2);
  DECLARE var_memo, freq_det VARCHAR(60);

DROP TABLE IF EXISTS `rental_statement`;
CREATE TABLE `rental_statement` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` date,
  `memo` varchar(60) DEFAULT NULL,
  `amount` decimal(8,2) DEFAULT 0.00,
  `payer` varchar(60) DEFAULT NULL,
  `balance` decimal(8,2) DEFAULT 0.00,
  PRIMARY KEY (`id`)
);

DROP TABLE IF EXISTS `temp_statement`;
CREATE TEMPORARY TABLE `temp_statement` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` date,
  `memo` varchar(60) DEFAULT NULL,
  `amount` decimal(8,2) DEFAULT 0.00,
  `payer` varchar(60) DEFAULT NULL,
  `balance` decimal(8,2) DEFAULT 0.00,
  PRIMARY KEY (`id`)
);

  SELECT freq_id, rentpa, startrentdate FROM rental
  WHERE id = rentalid
  INTO freq, rent, start_rent_date;

  SELECT freqdet FROM typefreq
  WHERE id = freq
  INTO freq_det;

  SET var_memo = CONCAT("rent due ", freq_det);
  SET vardate = start_rent_date;
  
  INSERT into temp_statement
  SELECT 0, vardate, var_memo, -rent/freq, "", 0;

  WHILE next_date(vardate, freq, 1) < calc_date DO
	INSERT into temp_statement
	SELECT 0, next_date(vardate, freq, 1), var_memo, -rent/freq, "", 0;
    SET vardate = next_date(vardate, freq, 1);
  END WHILE;
  
  INSERT into temp_statement
  SELECT 0, date, memo, amount, payer, 0 FROM money_item 
  WHERE num = rentalid AND cat_id = 63 AND date >= start_rent_date;
  

  SET @tot := 0;

  INSERT into rental_statement
  SELECT 0, date, memo, amount, payer, (@tot := @tot + amount) as balance 
  FROM temp_statement
  ORDER BY date, id;

END ;;
DELIMITER ;
