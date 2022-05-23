import os
import platform
import pyfiglet
ascii_banner = pyfiglet.figlet_format("Welcome to FSO RESET ONE TIME SETUP\n\n")
print(ascii_banner)

# To edit the path on destry.py
if platform.system() == 'Windows':
    print('*********** Windows OS detected ************************')
    terraform_dir = input('Please enter the path where you will like to save the Terraform API Key (eg C:\Terraform): ')
    terraform_file = input('Please enter the API Key for Terraform Cloud : ')
    te_dir = input('Please enter the path where you will like to save the Terraform API Key (eg C:\Thousand_eyes): ')
    te_file = input('Please enter the API Key for Thousand Eyes : ')
    user = input('Enter your Cisco User ID : ')
    aws_key = input('Enter your AWS Key ID : ')
    aws_access = input('Enter your AWS Access ID : ')
    terraform_dir = terraform_dir.replace('\\','/')
    terraform_path = f'{terraform_dir}/API.txt'
    te_dir = te_dir.replace('\\','/')
    te_path = f'{te_dir}/API.txt'
    print(terraform_dir,te_dir)
    with open('destroy.py','r') as edit:
        data = edit.read()
    data = data.replace('aaaa',f'{terraform_path}')
    data = data.replace('bbbb', f'{te_path}')
    with open('destroy.py','w') as file1:
        file1.write(data)
    os.mkdir(terraform_dir)
    os.chdir(terraform_dir)
    with open('API.txt', 'w') as file:
        file.write(terraform_file)
    os.mkdir(te_dir)
    os.chdir(te_dir)
    with open('API.txt', 'w') as file2:
        file2.write(te_file)
    os.chdir(f'C:/Users/{user}')
    os.mkdir('.aws')
    os.chdir(f'C:/Users/{user}/.aws')
    with open('config', 'w') as file5:
        file5.write(f'[default]\naws_access_key_id = {aws_key}\naws_secret_access_key = {aws_access}\nregion=us-west-1')
    print('******************SETUP COMPLETE***********************')

elif platform.system() == 'Darwin':
    print('*********** MAC OS detected ************************')
    terraform_dir = input('Please enter the path where you will like to save the Terraform API Key (eg C:\Terraform): ')
    terraform_file = input('Please enter the API Key for Terraform Cloud : ')
    te_dir = input('Please enter the path where you will like to save the Terraform API Key (eg C:\Thousand_eyes): ')
    te_file = input('Please enter the API Key for Thousand Eyes : ')
    user = input('Enter your Cisco User ID : ')
    aws_key = input('Enter your AWS Key ID : ')
    aws_access = input('Enter your AWS Access ID : ')
    terraform_dir = terraform_dir.replace('\\','/')
    terraform_path = f'{terraform_dir}/API.txt'
    te_dir = te_dir.replace('\\','/')
    te_path = f'{te_dir}/API.txt'
    print(terraform_dir,te_dir)
    with open('destroy.py','r') as edit:
        data = edit.read()
    data = data.replace('aaaa',f'{terraform_path}')
    data = data.replace('bbbb', f'{te_path}')
    with open('destroy.py','w') as file1:
        file1.write(data)
    os.mkdir(terraform_dir)
    os.chdir(terraform_dir)
    with open('API.txt', 'w') as file:
        file.write(terraform_file)
    os.mkdir(te_dir)
    os.chdir(te_dir)
    with open('API.txt', 'w') as file2:
        file2.write(te_file)
    os.chdir(f'C:/Users/{user}')
    os.mkdir('.aws')
    os.chdir(f'C:/Users/{user}/.aws')
    with open('config', 'w') as file5:
        file5.write(f'[default]\naws_access_key_id = {aws_key}\naws_secret_access_key = {aws_access}\nregion=us-west-1')
    print('******************SETUP COMPLETE***********************')


