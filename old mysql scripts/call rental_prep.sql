USE mjinn;

DROP TABLE IF EXISTS `rental_prep`;
CREATE TABLE `rental_prep` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` date,
  `memo` varchar(60) DEFAULT NULL,
  `amount` decimal(8,2) DEFAULT 0.00,
  `payer` varchar(60) DEFAULT NULL,
  `balance` decimal(8,2) DEFAULT 0.00,
  PRIMARY KEY (`id`)
);

INSERT into rental_prep
SELECT 0, date, memo, amount, payer, 0 FROM rental_trans WHERE rental_id = 3
;