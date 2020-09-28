INSERT INTO mjinn.extrent (rentcode, tenantname, propaddr, agentdetails, rentpa, arrears, lastrentdate, tenure, owner, source, status, extmanager_id)
SELECT RentCode, LEFT(TenantName,30), LEFT(PropAddress, 180), AgentDetails, Rent, Arrears, LastRentDate, Tenure, LEFT(Landlord, 15), Source, Status,
    CASE
        WHEN `Manager` = 'Sparrow' THEN 1
        WHEN `Manager` = 'EDS' THEN 2
        WHEN `Manager` = 'Hesmaloney' THEN 3
        WHEN `Manager` = 'HMCC' THEN 4
        WHEN `Manager` = 'MCS' THEN 5
        WHEN `Manager` = 'RMorgan' THEN 6
        WHEN `Manager` = 'Somerdawn' THEN 7
        WHEN `Manager` = 'Morgoed' THEN 8
        WHEN `Manager` = 'SWG' THEN 9
        WHEN `Manager` = 'HMG' THEN 10
    END
FROM yoda.rents_external
;