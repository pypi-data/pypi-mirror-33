# flake8: noqa
generate_usage = """
Usage:
     xld <connection-options> generate [directory] [command-options]

Description:
  Generate a Deployfile from a directory in the XL Deploy repository. 
  
Connection Options:     
    --url           Location of the XL Deploy server (including port). Overrides the value of the XL_DEPLOY_URL environment variable.
    --username      User name to use when authenticating with XL Deploy. Overrides the value of the XL_DEPLOY_USERNAME environment variable.
    --password      Password to use when authenticating with XL Deploy. Overrides the value of the XL_DEPLOY_PASSWORD environment variable. 
    
Command Options:     
    --debug         Show stacktrace if error.                                  

Usage examples:       
        xld --url {xld_url} --username {xld_username} --password {xld_password} generate /Infrastructure/AWS Environments/Cloud
        xld --url {xld_url} --username {xld_username} --password {xld_password} generate /Infrastructure/AWS Environments/Cloud > Deployfile
        
Documentation:   
    https://docs.xebialabs.com/xl-deploy/concept/xl-deploy-lightweight-cli.html        
"""
