#########################################################################################################################################################
#
# Name          :  IAMAudit.py
#
# Description   :  Generates credentials report for multiple accounts at once and saves it as excel file
#
# Written by    :  Rajesh Kumar
# 
# Updated by    :  Sarat Bobba
#
# Last Update   :  24/11/2017
#
#########################################################################################################################################################

import boto3
import time, datetime
import multiprocessing
import sys
import ConfigParser
import xlsxwriter
from botocore.exceptions import ClientError

def find_accesskey_age(aws_session, username):
    iam = aws_session.client('iam')
    res = iam.list_access_keys(UserName=username)
    activekeys = []
    for acckey in res['AccessKeyMetadata']:
        if acckey['Status'] == 'Active':
            activekeys.append(acckey['CreateDate'])
            activekeys = sorted(activekeys)
    if not activekeys:
        return "None"
    
    accesskeydate = activekeys[0]
    accesskeydate = accesskeydate.strftime("%Y-%m-%d %H:%M:%S")
    currentdate = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

    accesskeyd = time.mktime(datetime.datetime.strptime(accesskeydate, "%Y-%m-%d %H:%M:%S").timetuple())
    currentd = time.mktime(datetime.datetime.strptime(currentdate, "%Y-%m-%d %H:%M:%S").timetuple())

    active_days = (currentd - accesskeyd)/60/60/24
    return (int(round(active_days)))

def get_attached_user_policies(aws_session, username):
    iam = aws_session.client('iam')
    res = iam.list_attached_user_policies(UserName=username)
    usr_policy = []
    for policy in res['AttachedPolicies']:
        usr_policy.append(policy['PolicyName'])
    return "\n".join(usr_policy)

def list_acc_key_associated(aws_session, username):
    iam = aws_session.client('iam')
    res = iam.list_access_keys(UserName=username)
    accesskeys = {}
    for acckey in res['AccessKeyMetadata']:
        accesskeys[acckey['AccessKeyId']] = acckey['Status']
    return accesskeys

def find_password_age(aws_session, username):
    iam = aws_session.client('iam')
    try:
        resp = iam.get_login_profile(UserName=username)
        #print "Password age->", resp
        passdate = resp['LoginProfile']['CreateDate']
        passdate = passdate.strftime("%Y-%m-%d %H:%M:%S")
        currentdate = time.strftime("%Y-%m-%d %H:%M:%S")
        passwdate = time.mktime(datetime.datetime.strptime(passdate, "%Y-%m-%d %H:%M:%S").timetuple())
        currentd = time.mktime(datetime.datetime.strptime(currentdate, "%Y-%m-%d %H:%M:%S").timetuple())

        active_days = (currentd - passwdate)/60/60/24
        return (int(round(active_days)))
    except:
        return None
   
def get_last_used_key(aws_session, username):
    iam = aws_session.client('iam')
    res = iam.list_access_keys(UserName=username)
    activekeys = []
    for acckey in res['AccessKeyMetadata']:
        if acckey['Status'] == 'Active':
            last_used = iam.get_access_key_last_used(AccessKeyId=acckey['AccessKeyId'])['AccessKeyLastUsed'].get('LastUsedDate')
            if last_used:
                activekeys.append(last_used)
            else:
                continue
            activekeys = sorted(activekeys)
    if not activekeys:
        return "None"
    
    accesskeydate = activekeys[0]
    accesskeydate = accesskeydate.strftime("%Y-%m-%d %H:%M:%S")
    currentdate = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

    accesskeyd = time.mktime(datetime.datetime.strptime(accesskeydate, "%Y-%m-%d %H:%M:%S").timetuple())
    currentd = time.mktime(datetime.datetime.strptime(currentdate, "%Y-%m-%d %H:%M:%S").timetuple())

    active_days = (currentd - accesskeyd)/60/60/24
    if (int(round(active_days))) == 0:        
        return "Today"
    return (int(round(active_days)))

def get_last_activity(aws_session, username):
    iam = aws_session.client('iam')
    last_key_login = get_last_used_key(aws_session, username)    
    profdate = iam.get_user(UserName=username)['User'].get('PasswordLastUsed')
    if not profdate:
        return last_key_login
    profdate = profdate.strftime("%Y-%m-%d %H:%M:%S")
    currentdate = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    profiled = time.mktime(datetime.datetime.strptime(profdate, "%Y-%m-%d %H:%M:%S").timetuple())
    currentd = time.mktime(datetime.datetime.strptime(currentdate, "%Y-%m-%d %H:%M:%S").timetuple())

    active_days = int(round((currentd - profiled)/60/60/24))
    if last_key_login != "None" and last_key_login != "Today":
        active_days = active_days if last_key_login > active_days else last_key_login
        if active_days == 0:        
            return "Today"
        return active_days
    elif last_key_login == "None":
        if active_days == 0:
            return "Today"
        return active_days
    else:
        return last_key_login
		
		
def acount_wisse_xl_generator(data):
	profile = data.keys()[0]
	workbook = xlsxwriter.Workbook(str(profile)+".xlsx")
	worksheet = workbook.add_worksheet(profile)
	worksheet.set_tab_color('#2AA7A9')
	worksheet.autofilter('A1:O1')
	worksheet.set_column('A:O', 18)
	#Add format to cells.
	bold = workbook.add_format({'bold': True,'color':'#FFFFFF','border': 1})
	bold.set_bg_color('#2AA7A9')
	bold.set_align('center')
	bold.set_border_color('#2AA7A9')

	txt_format = workbook.add_format({'fg_color': '#FFFFFF','border': 1})
	txt_format.set_border_color('#2AA7A9')
	txt_format.set_align('center')
	txt_format.set_text_wrap()
	txt_format.set_align('vcenter')
	title = ['Account Number', 'Account Name', 'User name', 'Groups', 'Policies Attached', 'Access key age', 'Last activity', 'MFA', 'Creation time', 'Arn', 'Console Access', 'Console last sign-in', 'Active Access Key', 'Inactive Access Key', 'Access key last used']
	worksheet.write_row('A1', title, bold)
	start = 2
	for row in data[profile]:
		if not row[10]:
			worksheet.write_row('A'+str(start), row, txt_format)
			start = start+1
		
	workbook.close()
	
	
def write_results_to_excel(dataStore):
    workbook = xlsxwriter.Workbook("IAMAudit.xlsx")
    for data in dataStore: 
        if not data:
            continue
        acount_wisse_xl_generator(data) # It will generate indivual excel for acount wise.
	profile = data.keys()[0]
        worksheet = workbook.add_worksheet(profile)
        worksheet.set_tab_color('#2AA7A9')
        worksheet.autofilter('A1:O1')
        worksheet.set_column('A:O', 18)

        #Add format to cells.
        bold = workbook.add_format({'bold': True,'color':'#FFFFFF','border': 1})
        bold.set_bg_color('#2AA7A9')
        bold.set_align('center')
        bold.set_border_color('#2AA7A9')

        txt_format = workbook.add_format({'fg_color': '#FFFFFF','border': 1})
        txt_format.set_border_color('#2AA7A9')
        txt_format.set_align('center')
        txt_format.set_text_wrap()
        txt_format.set_align('vcenter')
        title = ['Account Number', 'Account Name', 'User name', 'Groups', 'Policies Attached', 'Access key age', 'Last activity', 'MFA', 'Creation time', 'Arn', 'Console Access', 'Console last sign-in', 'Active Access Key', 'Inactive Access Key', 'Access key last used']
        worksheet.write_row('A1', title, bold)
        start = 2
        for row in data[profile]:
            worksheet.write_row('A'+str(start), row, txt_format)
            start = start+1
    workbook.close()

def getAccountAliasName(aws_session):
    iam = aws_session.client('iam')
    paginator = iam.get_paginator('list_account_aliases')
    for response in paginator.paginate():
        if response['AccountAliases']:
            acc_name = response['AccountAliases'][0]
        else:
            acc_name = 'NA'
    return acc_name

def getSTSCred(accno):
    sts = session.client("sts")
    awsAccount_id = sts.get_caller_identity()["Account"]
    response = sts.assume_role(
        DurationSeconds=900,
        RoleArn='arn:aws:iam::'+accno+':role/readonly',
        RoleSessionName="ComcastCrossAssume"
    )
    return response['Credentials']

def getIAMUserMFA():
    iam = session.resource("iam", region_name='us-east-1')
    current_user = iam.CurrentUser()
    response = current_user.mfa_devices.filter(MaxItems=1)
    mfa = next(iter(response or []), None)
    return str(mfa.serial_number)

def get_credential_report(accno):
    try:
        accno = accno.strip()
        print "Creating Credential report for ->", accno
        creds = getSTSCred(accno)
        aws_session =  boto3.session.Session(aws_access_key_id=creds['AccessKeyId'],aws_secret_access_key=creds['SecretAccessKey'],aws_session_token=creds['SessionToken'])

        iam = aws_session.client('iam')
        response = iam.list_users()
        users_store = response['Users']
        auditList = []
        ret_data = {}
        if response['IsTruncated']:
            while  response['IsTruncated'] is True:
                response = iam.list_users(Marker=response['Marker'])
                users_store.extend(response['Users'])
        for userlist in users_store:
            userGroups = iam.list_groups_for_user(UserName=userlist['UserName'])
            print("Username: "  + userlist['UserName'])
            mfa_status = 'Virtual' if iam.list_mfa_devices(UserName=userlist['UserName'])['MFADevices'] else 'Not Enabled'
            associated_keys = list_acc_key_associated(aws_session, userlist['UserName'])
            active_keys = "\n".join([k for k,v in associated_keys.items() if v=="Active"])
            inactive_keys = "\n".join([k for k,v in associated_keys.items() if v=="Inactive"])
            group_assigned = ""
            password_age = find_password_age(aws_session, userlist['UserName'])
            last_activity = userlist.get('PasswordLastUsed')
            last_login = last_activity if password_age else "Never"
            if last_login and last_login != "Never":
                last_login = last_login.strftime("%Y-%m-%d %H:%M:%S")
            else:
                last_login = "Never"

            for groupName in userGroups['Groups']:
                group_assigned = group_assigned + groupName['GroupName'] + "\n"


            tempbuff = [
                accno,
                getAccountAliasName(aws_session),
                userlist['UserName'],
                group_assigned,
                get_attached_user_policies(aws_session, userlist['UserName']),
                find_accesskey_age(aws_session, userlist['UserName']),
                get_last_activity(aws_session, userlist['UserName']),
                mfa_status,
                userlist['CreateDate'].strftime("%Y-%m-%d %H:%M:%S"),
                userlist['Arn'],
                bool(password_age),
                last_login,
                active_keys,
                inactive_keys,
                get_last_used_key(aws_session, userlist['UserName'])
            ]
            auditList.append(tempbuff)
        ret_data[accno] = auditList
        return ret_data
    except Exception as e:
        print "Looks like you dont have IAM permission for the account "+accno
        print(e)

if len(sys.argv) < 2:
    print "Usage:: IAMAudit.py <inputConfig.ini>"
    exit()

inpfile = sys.argv[1] 
inputConfig = ConfigParser.ConfigParser(allow_no_value=True)
inputConfig.read(inpfile)
accNumList = inputConfig.options('agents')
access_key = inputConfig.get('governance','acc_key_id')
secret_key = inputConfig.get('governance','acc_sec_key')
session =  boto3.session.Session(aws_access_key_id=access_key,aws_secret_access_key=secret_key)


pool = multiprocessing.Pool()
results = list(pool.imap_unordered(get_credential_report, accNumList))
pool.close()
pool.join()

all_account_info = []
for result in results:
    profile = result.keys()[0]
    all_account_info.extend(result[profile])
    
results = [{'All':all_account_info}] + results
write_results_to_excel(results)
print "******************************* PROGRAM EXECUTED SUCCESSFULLY ******************************************"

