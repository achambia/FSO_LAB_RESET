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


def workspace():
    terraform_api = open("aaaa", "r")
    header = {"Authorization": f"{'Bearer'} {terraform_api.read()}", "Content-Type": "application/vnd.api+json"}
    print('Identifying the Workspace ID\n')
    response = requests.get(f'https://app.terraform.io/api/v2/organizations/Cisco-SRE/workspaces', headers=header)
    for x in response.json()['data']:
        if x['attributes']['name'] == pod_key[str(reset)]['workspace']:
            ws_id = (x['id'])
            cv_id = (x['relationships']['current-configuration-version']['data']['id'])
    return (ws_id, cv_id)

def ws_run():
    print('****************Connecting to Terraform to delete Infra ..****************\n ')
    terraform_api = open("aaaa", "r")
    header = {"Authorization": f"{'Bearer'} {terraform_api.read()}", "Content-Type": "application/vnd.api+json"}
    input_var = workspace()
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
    print('*********Destruction of the AWS Component Successful******************')

def te_tests():
    print('****************Connecting to TE to delete tests ..****************\n ')
    trigger = 0
    te_api = open("bbbb", "r")
    header = {"Authorization": f"{'Bearer'} {te_api.read()}", "accept":"application/json", "content-type":"application/json"}
    resposne = requests.get('https://api.thousandeyes.com/v6/tests.json', headers=header)
    for x in resposne.json()['test']:
        pod = pod_key[str(reset)]['podno']
        test_id = x['testId']
        test_type = x['type']
        if re.search(f'TeaStore-API-Call-GPO-FSO-Lab-{pod}.*',x['testName']):
            trigger = trigger +1
            respos = requests.post(f'https://api.thousandeyes.com/v6/tests/{test_type}/{test_id}/delete.json', headers=header)
            print(respos.status_code)
            if respos.status_code == 204:
                print('*****************TE Test deleted successfully .. *******************\n')
            else:
                print('!!!!! ERROR :: TE test not deleted successfully !!!!!!!!!!\n')
    if trigger == 0:
        print(f"****************** TE Tests not found for pod {reset}*******************\n")

def te_agents():
    print('****************Connecting to TE to delete Agents..****************\n ')
    te_api = open("bbbb", "r")
    trigger = 0
    header = {"Authorization": f"{'Bearer'} {te_api.read()}", "accept":"application/json", "content-type":"application/json"}
    resposne = requests.get('https://api.thousandeyes.com/v6/agents.json', headers=header)
    for x in (resposne.json()['agents']):
        pod = pod_key[str(reset)]['podno']
        if x['agentType'] == 'Enterprise':
            id = (x['agentId'])
            if re.search(f'GPO-FSO-Lab-{pod}.*', x['agentName']):
                trigger = trigger +1
                respo = requests.post(f'https://api.thousandeyes.com/v6/agents/{id}/delete.json', headers=header)
                if respo.status_code == 204:
                    print('****************TE Agent deleted successfully ..****************\n ')
                else:
                    print('!!!!!!!!! ERROR: TE Agent not deleted successfully !!!!!!!!!!!!!11 \n')
    if trigger == 0:
        print(f"****************** TE Agents not found for pod {reset}*******************\n")



def cloudformdel():
    print('*******************Connecting to AWS to clear Cloudformation stack******************* \n')
    trigger = 0
    client = boto3.client('cloudformation')
    response = client.describe_stacks()
    for x in (response['Stacks']):
        pod = pod_key[str(reset)]['podno']
        if re.search(f"GPO-FSO-Lab-{pod}.*EKS-Stack",x['StackName']):
            trigger = trigger + 1
            response = client.delete_stack(
                StackName=x['StackName'])
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                print('*******************Cloudformation stack deleted successfully******************* \n')
            else:
                print('!!!!!!!!! ERROR :: Cloudformation stack did not get deleted successfully !!!\n ')
    if trigger == 0:
        print(f"**********************Cloudformation Stack not created in AWS for pod {reset}***********************\n")




def ssm(inst_id):
    try:
        print('*************Initiating the Teardown script on the EC2 Instace*********\n')
        client = boto3.client('ssm')
        response = client.send_command(
            InstanceIds=[
                inst_id[0],
            ],
            DocumentName=pod_key[str(reset)]['document'],
        )
        cmd_id = response['Command']['CommandId']
        response1 = client.list_commands(
            CommandId=cmd_id,
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
    except Exception as e:
        if re.search('not in a valid state for account ', str(e)):
            print('*************Sleeping for 2 mins as Agent not ready for remote execution *************\n')
            time.sleep(120)
            ssm(inst_id)




def update_policy(ins_id):
    print('**************Connecting to AWS for Role updation to connect to SSM... *******************\n')
    iam = boto3.client('iam')
    ec2_name = ins_id[1]
    role = (re.sub('-VM','-EC2-Access-Role',ec2_name))
    response = iam.attach_role_policy(
        PolicyArn='arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore',
        RoleName=role
    )
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print('**************Permissions for Role updated successfully to connect to SSM... *******************\n')
    else:
        print('!!! ERROR :: Permissions for Role did not update successfully ...!!!!!\n')
    print("Sleeping for 30 secs")
    time.sleep(30)
    print('**************Connecting to AWS for rebooting EC2 to connect to SSM... *******************\n')
    client = boto3.client('ec2')
    client.reboot_instances(InstanceIds=[ins_id[0]])
    print("Sleeping for 30 secs")
    time.sleep(30)
    print('**************Successfully rebooted the EC2... *******************\n')

def ec2():
    print('**************Connecting to AWS to get InstanceID and Name of VM******************\n')
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
    print('***********************Instance ID retrieved***************************\n')
    return ec2_value

def cloud9():
    print("***************************Cloud9 Deletion Start************************\n")
    client = boto3.client('cloud9')
    response = client.list_environments(
    )
    for x in response['environmentIds']:
        repo = client.describe_environments(environmentIds=[x, ])
        if re.search(f".*{reset}-.*", repo['environments'][0]['name']):
            repo1 = client.delete_environment(environmentId=x)
            if repo1['ResponseMetadata']['HTTPStatusCode'] == 200:
                print('**********************Cloud9 Instance deleted Successfully **********************\n')
            else:
                print('!!!!!!!!!! ERROR :: Cloud9 Instance not deleted Successfully !!!!!!!!!!!!\n')




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
                else:
                    Podattaind.append("10")
                    Podattaind.remove(a[b - 1])


            elif (h[j - 1] == "1") and (a[b] == "1"):
                if '-' in h:
                    Podattaind.pop(b - 1)
                    Podattaind.append("11")
                elif ',' in h:
                    Podattaind.remove(a[b - 1])
                    Podattaind.append("11")
                else:
                    Podattaind.append("11")
                    Podattaind.remove(a[b - 1])



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
    print(f'*******************Destruction of Pod {reset} initiated\n')
    ins_id = ec2()
    update_policy(ins_id)
    cloudformdel()
    te_tests()
    te_agents()
    ssm(ins_id)
    ws_run()
    cloud9()
    print(f"***************** Pod {reset}  Deleted Successfully  :-) *************")



