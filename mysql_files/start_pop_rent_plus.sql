USE mjinn;

INSERT INTO mjinn.agent (id, detail, email, note, code)
SELECT 0, AgentDetails, AgentEmail, AgentTel, AgentCode
FROM yoda.agents
