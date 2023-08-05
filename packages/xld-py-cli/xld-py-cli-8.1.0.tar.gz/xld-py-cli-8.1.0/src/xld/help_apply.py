# flake8: noqa
apply_usage = """
Usage:
     xld <connection-options> apply Deployfile [command-options]

Description:
  Apply a Deployfile to the XL Deploy repository that creates or updates configuration item(s) and/or uploads or deploys application(s) to environment(s).
  Deployfile is a Groovy file that describes the desired state of infrastructure, environment and/or application configuration items (CIs) in the XL Deploy repository. When an application is included, the configuration item will be created and the application will be deployed to the target environment. 
  
  
Connection Options:     
    --url           Location of the XL Deploy server (including port). Overrides the value of the XL_DEPLOY_URL environment variable.
    --username      User name to use when authenticating with XL Deploy. Overrides the value of the XL_DEPLOY_USERNAME environment variable.
    --password      Password to use when authenticating with XL Deploy. Overrides the value of the XL_DEPLOY_PASSWORD environment variable. 
    
Command Options:    
    --debug         Show stacktrace if error.                                  

Usage examples:       
        xld --url {xld_url} --username {xld_username} --password {xld_password} apply Deployfile
        
Documentation:   
    https://docs.xebialabs.com/xl-deploy/concept/xl-deploy-lightweight-cli.html                 
"""