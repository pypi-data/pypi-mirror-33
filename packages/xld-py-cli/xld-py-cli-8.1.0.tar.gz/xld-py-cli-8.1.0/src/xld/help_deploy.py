# flake8: noqa
deploy_usage = """
Usage:
     xld <connection-options> deploy [command-options]

Description:
  Deploy a package to an environment. 
  
Connection Options:     
    --url            Location of the XL Deploy server (including port). Overrides the value of the XL_DEPLOY_URL environment variable.
    --username       User name to use when authenticating with XL Deploy. Overrides the value of the XL_DEPLOY_USERNAME environment variable.
    --password       Password to use when authenticating with XL Deploy. Overrides the value of the XL_DEPLOY_PASSWORD environment variable. 
    
Command Options:     
    --package-id     Full ID of the application to deploy, as displayed in XL Deploy repository.
    --environment-id Full ID of the environment to provision to given application, as displayed in XL Deploy repository.
    --debug          Show stacktrace if error.
    
Usage examples:       
        xld --url {xld_url} --username {xld_username} --password {xld_password} deploy PACKAGE_ID ENVIRONMENT_ID
        xld --url {xld_url} --username {xld_username} --password {xld_password} deploy --package-id PACKAGE_ID --environment-id ENVIRONMENT_ID
        
Documentation:   
    https://docs.xebialabs.com/xl-deploy/concept/xl-deploy-lightweight-cli.html        
"""