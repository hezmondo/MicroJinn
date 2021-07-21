USE mjinn;

INSERT INTO manager_external VALUES (1,'Sparrow','Ben Sparrow, Trevelloe, Paul, Penzance, Cornwall TR19 6NS  Tel: 01736 731194  Mobile: 07717 021433  email: brwsp@tiscali.co.uk'),(2,'EDS','East Devon (Securities) Limited, Paxfield, Higher Broad Oak Road, West Hill, Ottery St. Mary, Devon EX11 1XJ.  Tel: 01404 815144   email hmcc.securities@yahoo.co.uk'),(3,'Hezmaloney','Hesmondhalgh & Maloney, Hawthorn Dene, School Lane, West Hill, Ottery St. Mary, Devon EX11 1UP'),(4,'HMCC','HMCC (Securities) Limited, Paxfield, Higher Broad Oak Road, West Hill, Ottery St. Mary, Devon EX11 1XJ.  Tel: 01404 815144   email hmcc.securities@yahoo.co.uk'),(5,'MCS','MCS Property Ltd, Melton Court, Rockbeare Hill, Exeter, Devon  EX5 2EZ. Tel 07518 052611  Fax 01404 822474  email info@mcsproperty.org.uk'),(6,'RMorgan','Roger Morgan, Woodside, Farringdon, Exeter EH5 2CA Tel: 01395 232113  email: art@eclipse.co.uk'),(7,'Somerdawn','Somerdawn Limited, Rockford Lodge, 161 Upper Woodcote Road, Caversham, Reading RG4 7JR Tel: 0118 947 1781  email: somerdawn1@gmail.com'),(8,'Morgoed','Morgoed Estates Ltd, Clungunford, Craven Arms SY7 0QL  Tel: 01588 660779  email: david.roberts@morgoedestates.com  Co reg no: 03273896'),(9,'SWGR','South West Ground Rents, Melton Court, Rockbeare Hill, Exeter, Devon  EX5 2EZ. Tel: 07547371857  email: SouthwestGroundRents@gmail.com'),(10,'HMG','HMG Securities Limited, Paxfield, Higher Broad Oak Road, West Hill, Ottery St. Mary, Devon EX11 1XJ.  Tel: 01404 815144   email: hmgsecurities@gmail.com  Co reg no: 09887347');

INSERT INTO rent_external (rentcode, tenantname, propaddr, agentdetail, rentpa, arrears, lastrentdate, tenure, owner, source, status, extmanager_id)
SELECT RentCode, LEFT(TenantName,30), LEFT(PropAddress, 180), AgentDetails, Rent, Arrears, LastRentDate, Tenure, LEFT(Landlord, 30), Source, Status,
    CASE
        WHEN `Manager` = 'Sparrow' THEN 1
        WHEN `Manager` = 'EDS' THEN 2
        WHEN `Manager` = 'Hezmaloney' THEN 3
        WHEN `Manager` = 'HMCC' THEN 4
        WHEN `Manager` = 'MCS' THEN 5
        WHEN `Manager` = 'RMorgan' THEN 6
        WHEN `Manager` = 'Somerdawn' THEN 7
        WHEN `Manager` = 'Morgoed' THEN 8
        WHEN `Manager` = 'SWGR' THEN 9
        WHEN `Manager` = 'HMG' THEN 10
    END
FROM yoda.rents_external
; 

