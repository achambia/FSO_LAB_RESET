# FSO_LAB_RESET
update 
# Users need to install latest version of Python, Git and import the below modules 
1. boto3 
2. requests
3. pyfiglet

In order to Install Python go to below URL 
https://www.python.org/downloads/

After Installing python , run the below commands to install the modules
pip3 install boto3
pip3 install requests
pip3 install pyfiglet

In order to Install Git
1. Download git from the URL https://git-scm.com/book/en/v2/Getting-Started-Installing-Git
2. Install git , keep everything to default. 
3. After installation go to desktop , right click >> Git Bash Here
4. Move and create a directory where you want to pull the reset script
5. Clone the repo using the command "git clone https://github.com/achambia/FSO_LAB_RESET"
6. move to FSO_LAB_RESET dir using "cd FSO_LAB_RESET"
7. Checkout the main branch using the cmd "git checkout main"

NOTE: Please use IDE like IDLE (Comes default with python) as it will help to catch for any errors. 

# Users need to Initially run one_time_run.py .. 

This will make the User enter the API details for TE, Terraform and AWS

In order get the API token for Terraform go to Terraform >> Click on User icon on top right >> User Settings >>  Token >> Create an API token >> Note the Token

In order get the API token for TE go to TE >> Login with your username and password >> Account Settings >> Users and Roles >> User API Tokens >> OAuth Bearer Token >> Note the token

For AWS , please ask the admin to generate keys for your account

# Users post that can run the destroy.py from their workstation any time.

