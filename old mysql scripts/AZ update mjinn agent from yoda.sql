#SELECT r.rentcode, a.agdetails, a.agemail, ya.AgentCode, ya.AgentDetails 
#FROM 
UPDATE
mjinn.rent r 
LEFT JOIN mjinn.agent a
ON r.agent_id = a.id
LEFT JOIN yoda.link l
ON r.rentcode = l.RentCode
LEFT JOIN yoda.agents ya
ON l.AgentCode = ya.AgentCode 
#SET a.code = ya.AgentCode
SET a.agdetails = CONCAT(ya.AgentDetails, " tel: ", ya.AgentTel),
a.agemail = ya.AgentEmail
;