USE samjinn;
CALL lex_get_valuation("ZASH%", 5.0, 6.5, 250.0, 100, 13.0, 17);
SELECT * FROM lease_valuations;
