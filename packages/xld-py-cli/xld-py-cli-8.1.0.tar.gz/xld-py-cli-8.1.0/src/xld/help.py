# flake8: noqa
help_message = """
Usage:
     xld <connection-options> <command> [command-options]
     
Commands:
    apply           Apply a Deployfile to the XL Deploy repository.
    deploy          Deploy a package to an environment.
    generate        Generate a Deployfile from a directory in the XL Deploy repository.
    help            Show help.
    version         Show version.
    encrypt         Encrypt plain text for password/sensitive Deployfile property value.

Connection Options:     
    --url           Location of the XL Deploy server (including port). Overrides the value of the XL_DEPLOY_URL environment variable.
    --username      User name to use when authenticating with XL Deploy. Overrides the value of the XL_DEPLOY_USERNAME environment variable.
    --password      Password to use when authenticating with XL Deploy. Overrides the value of the XL_DEPLOY_PASSWORD environment variable.

Command Options:
    --debug         Show stacktrace if error.

Documentation:   
    https://docs.xebialabs.com/xl-deploy/concept/xl-deploy-lightweight-cli.html 
"""
