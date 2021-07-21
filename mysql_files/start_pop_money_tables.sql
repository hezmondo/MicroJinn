USE mjinn;

INSERT INTO `money_category` SELECT ID, Category FROM yoda.bank_category

--INSERT INTO `money_account` VALUES (1,'Santander','Hesmondhalgh & Maloney','09-01-50','01513656','Santander RHDM'),(2,'Natwest','R Hesmondhalgh & D Maloney','53-50-55','11219270','Natwest RHDM'),(3,'Santander','Hesmaloney Limited','09-01-50','05792215','Santander HML 2215'),(4,'Natwest','Richard Hesmondhalgh','53-50-55','11219262','Natwest RH'),(5,'Virgin','Richard Hesmondhalgh','08-61-15','54628U-00332','Virgin RH'),(6,'NSI','Richard Hesmondhalgh','11-11-11','1234','NSI RH'),(7,'PC','Petty Cash','11-11-11','1234','Petty cash'),(8,'Natwest','Secure Equity Assets Management Ltd.','11-11-11','1234','Natwest SEAM'),(9,'Lloyds TSB','D A Maloney','11-11-11','1234','Lloyds DM'),(10,'Paypal','Richard Hesmondhalgh','11-11-11','1234','Paypal'),(11,'Santander','Secure Equity Assets Management Ltd.','09-01-50','05789370','Santander SEAM'),(13,'Virtual','Hesmondhalgh & Maloney','11-11-11','1234','Virtual bank'),(14,'Santander','Hesmaloney Limited','09-01-50','05792207','Santander HML 2207'),(15,'HSBC','Richard Hesmondhalgh','40-24-28','61441582','HSBC RH'),(16,'Nationwide','Richard Hesmondhalgh','11-11-11','1234','Nationwide RH'),(17,'HSBC','R Hesmondhalgh & Nicholas Lowe','11-11-11','1234','HSBC RH & NL'),(18,'OldhamPC','OldhamPC','11-11-11','1234','Petty cash Oldham'),(19,'Visa','Visa','11-11-11','1234','Visa RH'),(20,'Virgin','D A Maloney','11-11-11','1234','Virgin DM'),(21,'Yorkshire','R Hesmondhalgh & D Maloney','11-11-11','1234','Yorkshire RHDM'),(22,'NSI','D A Maloney','11-11-11','1234','NSI DM');
INSERT INTO `money_account`
SELECT BankType, BankName, BankAccountName, BankSortCode, BankAccountNumber, BankDescription
FROM yoda.types_bank

INSERT into money_item
SELECT 0, Num, Date, Payee, Amount, Memo, Cat,
CASE
	WHEN Recon = "C" THEN 0
    ELSE 1
END,
Account
FROM yoda.bank_transaction
WHERE Cat != 34
AND Date >= "2021-05-09"
ORDER BY Date
;

