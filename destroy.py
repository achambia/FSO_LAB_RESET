import requests
import re
import time
import json
import boto3
import pyfiglet
import sys
pod_key = {'1':{'podno':'01','workspace':'GPO-FSO-EKS-LAB-1','document':'destroy_pod_1'},
           '2': {'podno': '02', 'workspace': 'GPO-FSO-EKS-LAB-2', 'document': 'destroy_pod_2'},
           '3': {'podno': '03', 'workspace': 'GPO-FSO-EKS-LAB-3', 'document': 'destroy_pod_3'},
           '4': {'podno': '04', 'workspace': 'GPO-FSO-EKS-LAB-4', 'document': 'destroy_pod_4'},
           '5': {'podno': '05', 'workspace': 'GPO-FSO-EKS-LAB-5', 'document': 'destroy_pod_5'},
           '6': {'podno': '06', 'workspace': 'GPO-FSO-EKS-LAB-6', 'document': 'destroy_pod_6'},
           '7': {'podno': '07', 'workspace': 'GPO-FSO-EKS-LAB-7', 'document': 'destroy_pod_7'},
           '8': {'podno': '08', 'workspace': 'GPO-FSO-EKS-LAB-8', 'document': 'destroy_pod_8'},
           '9': {'podno': '09', 'workspace': 'GPO-FSO-EKS-LAB-9', 'document': 'destroy_pod_9'},
           '10': {'podno': '10', 'workspace': 'GPO-FSO-EKS-LAB-10', 'document': 'destroy_pod_10'},
           '11':{'podno':'11','workspace':'SWAT-FSO-TEST','document':'destroy_pod_11'},
           }
terraform_api = open("aaaa", "r")
te_api = open("bbbb", "r")

def workspace():
    header = {"Authorization": f"{'Bearer'} {terraform_api.read()}", "Content-Type": "application/vnd.api+json"}
    print('Identifying the Workspace ID\n')
    response = requests.get(f'https://app.terraform.io/api/v2/organizations/Cisco-SRE/workspaces', headers=header)
    for x in response.json()['data']:
        if x['attributes']['name'] == pod_key[str(reset)]['workspace']:
            ws_id = (x['id'])
            cv_id = (x['relationships']['current-configuration-version']['data']['id'])
    return (ws_id, cv_id)

def ws_run():
    header = {"Authorization": f"{'Bearer'} {terraform_api.read()}", "Content-Type": "application/vnd.api+json"}
    input_var = workspace()
    print(input_var)
    print('Initiating run on the workspace \n')
    run_data = json.dumps({"data": {"attributes": {"message": "Trigered via API", 'auto-apply': True, 'is-destroy': True},"type": "runs","relationships": {"workspace": {"data": {"id": input_var[0]}}}}})
    response = requests.post('https://app.terraform.io/api/v2/runs', headers=header, data= run_data)
    print('Workspace plan applied .. Resources being destroyed .. It takes around 7 minutes for resources to be destroyed. \n')
    run_id = response.json()['data']['id']
    status = response.json()['data']['attributes']['status']
    print('sleeping for 5 mins \n')
    time.sleep(300)
    while status != 'applied':
        if status == 'errored':
            print('Terraform code failed .. Please check manually ..')
            break
        response = requests.get(f' https://app.terraform.io/api/v2/runs/{run_id}', headers=header)
        status = response.json()['data']['attributes']['status']
        print(f'Terraform is {status} config, script will sleep for 50 secs ..\n')
        time.sleep(50)
    print('*********Destruction of the Pod Complete******************')

def te_tests():
    header = {"Authorization": f"{'Bearer'} {te_api.read()}", "accept":"application/json", "content-type":"application/json"}
    resposne = requests.get('https://api.thousandeyes.com/v6/tests.json', headers=header)
    for x in resposne.json()['test']:
        pod = pod_key[str(reset)]['podno']
        test_id = x['testId']
        test_type = x['type']
        if re.search(f'TeaStore-API-Call-GPO-FSO-Lab-{pod}.*',x['testName']):
            respos = requests.post(f'https://api.thousandeyes.com/v6/tests/{test_type}/{test_id}/delete.json', headers=header)
            if respos.status_code == 204:
                print('*****************TE Test deleted successfully .. *******************\n')
            else:
                print('!!!!! ERROR :: TE test not deleted successfully !!!!!!!!!!\n')

def te_agents():
    te_api = open("C:\\TE\API.txt", "r")
    header = {"Authorization": f"{'Bearer'} {te_api.read()}", "accept":"application/json", "content-type":"application/json"}
    resposne = requests.get('https://api.thousandeyes.com/v6/agents.json', headers=header)
    for x in (resposne.json()['agents']):
        pod = pod_key[str(reset)]['podno']
        if x['agentType'] == 'Enterprise':
            id = (x['agentId'])
            if re.search(f'GPO-FSO-Lab-{pod}.*', x['agentName']):
                respo = requests.post(f'https://api.thousandeyes.com/v6/agents/{id}/delete.json', headers=header)
                if respo.status_code == 204:
                    print('****************TE Agent deleted successfully ..****************\n ')
                else:
                    print('!!!!!!!!! ERROR: TE Agent not deleted successfully !!!!!!!!!!!!!11 \n')



def cloudformdel():
    client = boto3.client('cloudformation')
    response = client.describe_stacks()
    for x in (response['Stacks']):
        pod = pod_key[str(reset)]['podno']
        if re.search(f"GPO-FSO-Lab-{pod}.*EKS--Stack",x['StackName']):
            response = client.delete_stack(
                StackName=x['StackName'])
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                print('*******************Cloudformation stack deleted successfully******************* \n')
            else:
                print('!!!!!!!!! ERROR :: Cloudformation stack did not get deleted successfully !!!\n ')


def ssm(inst_id):
    client = boto3.client('ssm')
    response = client.send_command(
        InstanceIds=[
            inst_id[0],
        ],
        DocumentName=pod_key[str(reset)]['document'],
    )
    cmd_id = response['Command']['CommandId']
    response1 = client.list_commands(
        CommandId = cmd_id,
    )
    print('Command ran successfully.. sleeping for 6 Mins')
    time.sleep(360)
    while response1['Commands'][0]['Status'] != 'Success':
        if response1['Commands'][0]['Status'] == 'Failed':
            print('Agent cleanup script failed')
            break
        print('Agents not removed yet .. sleeping for 30 secs')
        time.sleep(30)
        response1 = client.list_commands(
            CommandId=cmd_id,
        )
    print('Agents removed successfully')


def update_policy(ins_id):
    iam = boto3.client('iam')
    ec2_name = ins_id[1]
    role = (re.sub('-VM','-EC2-Access-Role',ec2_name))
    response = iam.attach_role_policy(
        PolicyArn='arn:aws:iam::aws:policy/service-role/AmazonEC2RoleforSSM',
        RoleName=role
    )
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print('**************Permissions for Role updated successfully to connect to SSM... *******************\n')
    else:
        print('!!! ERROR :: Permissions for Role did not update successfully ...!!!!!\n')

def ec2():
    ec2_value = []
    ec2 = boto3.client('ec2')
    response = ec2.describe_instances()['Reservations']
    for x in response:
        pod = pod_key[str(reset)]['podno']
        for y in (x)['Instances']:
            for z in y['Tags']:
                if z['Key'] == 'Name':
                    if re.search(f'{pod}-.*-VM', z['Value']):
                        ec2_value.append(y['InstanceId'])
                        ec2_value.append(z['Value'])
    return ec2_value





Number = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9','10']
PodNumber = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10','11']
Pod_to_rest = []
Podattaind = []
h = []
ascii_banner = pyfiglet.figlet_format("Welcome to FSO LAB RESET UTILITY\n\n")
print(ascii_banner)

a = list(input("PLEASE ENTER THE POD YOU WANT TO RESET . FOR MULTIPLE POD RESET USE , OR - (EG. 1-3,5) : "))

for b in range(len(a)):
    if a[b] == "-":
        Podattaind.append("-")
        h.append(a[b])
    elif a[b] == ",":
        h.append(",")
    elif (a[b] == "1") or (a[b] == "2") or (a[b] == "3") or (a[b] == "4") or (a[b] == "5") or (a[b] == "6") or (
            a[b] == "7") or (a[b] == "8") or (a[b] == "9") or (a[b] == "0"):
        if len(h) == 0:
            h.append(a[b])
            Podattaind.append(a[b])

        elif len(h) != 0:
            j = int(len(h))

            h.append(a[b])
            if (h[j - 1] == "1") and (a[b] == "0"):
                if '-' in h:
                    Podattaind.pop(b - 1)
                    Podattaind.append("10")
                elif ',' in h:
                    Podattaind.remove(a[b - 1])
                    Podattaind.append("10")


            elif (h[j - 1] == "1") and (a[b] == "1"):
                if '-' in h:
                    Podattaind.pop(b - 1)
                    Podattaind.append("11")
                elif ',' in h:
                    Podattaind.remove(a[b - 1])
                    Podattaind.append("11")


            elif (h[j - 1] == "1") or (h[j - 1] == "2") or (h[j - 1] == "3") or (h[j - 1] == "4") or (
                    h[j - 1] == "5") or (h[j - 1] == "6") or (h[j - 1] == "7") or (h[j - 1] == "8") or (
                    h[j - 1] == "9") or (h[j - 1] == "0"):
                Podattaind.remove(a[b - 1])

            else:
                Podattaind.append(a[b])

for x in range(len(Podattaind)):
    if Podattaind[x] == '-':
        d = int(Podattaind[x - 1])
        e = int(Podattaind[x + 1])
        for z in range(d + 1, e):
            f = str(z)
            Pod_to_rest.append(f)
    else:
        Pod_to_rest.append(Podattaind[x])
if len(Pod_to_rest) == int(0):
    print("\n\nINVALID POD NUMBER SELECTED\n\n")
    sys.exit()
for reset in Pod_to_rest:
    ins_id =ec2()
    update_policy(ins_id)
    cloudformdel()
    te_tests()
    te_agents()
    client =  boto3.client('ssm')
    response = client.describe_instance_information(
    )
    for x in response['InstanceInformationList']:
        while x['InstanceId'] != ins_id[0] and x['PingStatus'] != 'Online':
            print("Wating for Instance to be controlled by SSM .. SLeeping for 60 secs")
            time.sleep(60)
            response = client.describe_instance_information(
            )
            for y in response['InstanceInformationList']:
                if y['InstanceId'] == ins_id[0] and y['PingStatus'] == 'Online':
                    break
            x =y
    ssm(ins_id)
    ws_run()


