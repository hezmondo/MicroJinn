INSERT INTO mjinn.lease_uplift_type
SELECT 0, UpliftType, UpliftYears, UpliftMethod, UpliftValue FROM yoda.lease_uplift_types;

INSERT INTO mjinn.lease_extension
SELECT 0, RentCode, LexDate, Premium FROM yoda.lease_extensions

INSERT INTO mjinn.lease_relativity
SELECT 0, YearsUnexpired, relativity FROM yoda.lease_relativity