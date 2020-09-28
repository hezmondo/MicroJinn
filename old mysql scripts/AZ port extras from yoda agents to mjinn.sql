INSERT INTO mjinn.agent (id, agdetails, agemail, agnotes)
SELECT 0, CONCAT(a.AgentDetails, " tel: ", a.AgentTel), a.AgentEmail, ""
FROM yoda.agents a
RIGHT JOIN yoda.link l
ON l.AgentCode = a.Agentcode
WHERE l.RentCode IN
(SELECT rentcode FROM mjinn.rent
WHERE mailto_id < 3
AND agent_id = 1
AND rentcode != "ZABV10"
)
