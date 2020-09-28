UPDATE mjinn.loan_trans
SET memo = REPLACE (memo, "Loan interest repayment", "Interest payment")
;