# IAM_Audit
Auditing IAM Users 
You need Access and Secrect Key \
You need a ReadOnly Role - This can be Local Role or Cross Account Role \
Replace with your Role in ( readonly ; Line no 203 ) :- RoleArn='arn:aws:iam::'+accno+':role/readonly'
Execute as  :-  python IAMAudit_v3.py  inputConfig.ini \
IAMAudit_v3.py :– Contains the Code \
inputConfig.ini :-  Contains list of AWS accounts to be scanned for IAM details  +  Your Access Key and Secret Key  ( Just replace with your Keys and Your AWS Accounts – Rest shouldn’t be modified )
Note :- You should have necessary permissions to scan IAM in all AWS accounts \
Output :- This will generate three types of Excel sheets ) \
IAMAudit.Xlsx  (   Provide details of all accounts in One Tab ;  ++ details of Individual accounts from second Tab \


 
