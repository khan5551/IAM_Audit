# IAM_Audit
1. For Auditing IAM Users you need following 
2. You need Access and Secrect Key 
3. You need a ReadOnly Role - This can be Local Role or Cross Account Role 
4. Replace with your Role in ( readonly ; Line no 203 ) :- RoleArn='arn:aws:iam::'+accno+':role/readonly'
5. Execute as  :-  python IAMAudit_v3.py    inputConfig.ini 
6. IAMAudit_v3.py :– Contains the Code 
7. inputConfig.ini :-  Contains list of AWS accounts to be scanned for IAM details  +  Your Access Key and Secret Key  ( Just replace with    your Keys and Your AWS Accounts – Rest shouldn’t be modified )
8. Note :- You should have necessary permissions to scan IAM in all AWS accounts 
9. Output :- This will generate three types of Excel sheets ) 
10. IAMAudit.Xlsx  (   Provide details of all accounts in One Tab ;  ++ details of Individual accounts from second Tab 
11. Output with following details 
a) Account Number	\
b) Account Name	\
c) User name \
d) Groups \
e) Policies Attached \
f) Access key age \
g) Last activity \
h) MFA	 \
i) Creation time	\
j) Arn	\
k) Console Access	\
l) Console last sign-in	\
m) Active Access Key	\
n) Inactive Access Key	\
o) Access key last used 


 
