INSERT INTO mjinn.agent (id, agdetails, agemail, agnotes, code)
SELECT 0, CONCAT(a.AgentDetails, " tel: ", a.AgentTel), a.AgentEmail, "", a.AgentCode
FROM yoda.agents a
RIGHT JOIN yoda.headrents h
ON h.AgentCode = a.Agentcode
WHERE h.Status IN ("A", "S")
GROUP BY a.AgentCode


INSERT INTO mjinn.agent (id, agdetails, agemail, agnotes, code)
SELECT 0, CONCAT(a.AgentDetails, " tel: ", a.AgentTel), a.AgentEmail, "", a.AgentCode
FROM yoda.agents a
RIGHT JOIN yoda.link l
ON l.AgentCode = a.Agentcode
WHERE l.RentCode IN
(SELECT rentcode FROM mjinn.rent)
GROUP BY a.AgentCode;


