CREATE FUNCTION `next_rent_date`(rentid int, rentype int) RETURNS date
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
END