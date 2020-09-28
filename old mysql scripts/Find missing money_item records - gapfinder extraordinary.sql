SELECT
 CONCAT(z.expected, IF(z.got-1>z.expected, CONCAT(' thru ',z.got-1), '')) AS missing
FROM (
 SELECT
  @rownum:=@rownum+1 AS expected,
  IF(@rownum=mjinn.money_item.id, 0, @rownum:=mjinn.money_item.id) AS got
 FROM
  (SELECT @rownum:=0) AS a
  JOIN mjinn.money_item
  ORDER BY id
 ) AS z
WHERE z.got!=0;