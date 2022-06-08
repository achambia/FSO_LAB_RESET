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
    print('****************Connecting to Terraform to create Infra ..****************\n ')
    terraform_api = open("aaaa", "r")
    header = {"Authorization": f"{'Bearer'} {terraform_api.read()}", "Content-Type": "application/vnd.api+json"}
    input_var = workspace()
    print('Initiating run on the workspace \n')
    run_data = json.dumps({"data": {"attributes": {"message": "Trigered via API",'auto-apply': True},"type":"runs","relationships": {"workspace": {"data": {"type": "workspaces","id": input_var[0]}},"configuration-version": {"data": {"type": "configuration-versions","id": [input_var[1]]}}}}})
    response = requests.post('https://app.terraform.io/api/v2/runs', headers=header, data= run_data)
    print('Workspace plan applied, sleeping for 6 mins \n')
    run_id = response.json()['data']['id']
    response = requests.get(f' https://app.terraform.io/api/v2/runs/{run_id}', headers=header)
    status = response.json()['data']['attributes']['status']
    time.sleep(360)
    while status != 'applied':
        if status == 'errored':
            print('Terraform code failed .. Please check manually ..')
            break
        response = requests.get(f' https://app.terraform.io/api/v2/runs/{run_id}', headers=header)
        status = response.json()['data']['attributes']['status']
        print(f'Terraform is {status} config, script will sleep for 50 secs ..\n')
        time.sleep(50)
    print('Apply complete.. Will Need Manual intervention to spin Cloud9 as AWS does not allow this via code')


def ec2():
    inst_id = []
    print('Logging into AWS to get the Instance name and Public DNS \n')
    ec2 = boto3.client('ec2')
    response = ec2.describe_instances()['Reservations']
    for x in response:
        pod = pod_key[str(reset)]['podno']
        for y in (x)['Instances']:
            for z in y['Tags']:
                if z['Key'] == 'Name':
                    if re.search(f'{pod}-.*-VM', z['Value']):
                        inst_id.append(y['InstanceId'])
                        inst_id.append(y['PublicDnsName'])
                        inst_id.append(z['Value'])
    return inst_id


def cloud9_create():
    ec2_values = ec2()
    dns = ec2_values[1]
    cloud = ec2_values[2]
    cloud = re.sub('-VM','-Cloud9',cloud)
    print(f'Public DNS : {dns}, Cloud9 instance name : {cloud}\n\n Please log into AWS console Cloud9 "https://us-west-1.console.aws.amazon.com/cloud9/home/create">>\n Create Environment >> \nEnter the name from Cloud9 Instance Name >> \nSelect SSH and enter the DNS name >> Click create environemt >> \nCopy the URL from the newly opened tab\n')
    ide = input('Enter the URL for cloud9 from the AWS: ')
    client = boto3.client('cloud9')
    response = client.list_environments()
    print('Changing the Permission in Cloud9 to enable access to fso-lab-user \n')
    time.sleep(30)
    for x in response['environmentIds']:
        if client.describe_environments(environmentIds=[x])['environments'][0]['name'] == cloud:
            response = client.create_environment_membership(
                environmentId=x,
                userArn=f'arn:aws:iam::cccc:user/fso-lab-user',
                permissions='read-write'
            )
    print('Successfully modified the permission\n')
    print(f'User Access \n cloud 9 Url : {ide}\n')
    print('Lab Guide: www.fsolabs.net')


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
    ws_run()
    ec2()
    cloud9_create()
