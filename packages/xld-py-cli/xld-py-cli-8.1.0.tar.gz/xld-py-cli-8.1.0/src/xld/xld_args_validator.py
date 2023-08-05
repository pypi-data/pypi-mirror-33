from __future__ import print_function
import sys
from fire import core
from fire import trace
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


class XldArgsValidator:

    __validation_error_msg = "Missing required parameter --{param} or Environment variable {env_variable}"
    __validation_url_malformated_error_msg = "'{url}' string has no URL scheme specifier and/or Network location part."
    __validation_url_parse_error_msg = "Failed to parse '{url}' string as a Uniform Resource Locator (URL)"
    __validation_url_invalid_port_msg = "'{url}' string has invalid port number."

    XL_DEPLOY_URL = 'XL_DEPLOY_URL'
    XL_DEPLOY_USERNAME = 'XL_DEPLOY_USERNAME'
    XL_DEPLOY_PASSWORD = 'XL_DEPLOY_PASSWORD'

    def __init__(self):
        pass

    def validate(self, url, username, password):
        error_trace = trace.FireTrace(self, verbose=True, show_help=True, show_trace=True)
        self.__is_valid_value(url, 'url', self.XL_DEPLOY_URL, error_trace)
        self.__is_valid_value(username, 'username', self.XL_DEPLOY_USERNAME, error_trace)
        self.__is_valid_value(password, 'password', self.XL_DEPLOY_PASSWORD, error_trace)
        if error_trace.HasError():
            # log the error trace on console, as raising the Exception does not log it on its own.
            self.__print_validation_errors(error_trace)
            raise core.FireExit(2, error_trace)

    def __is_valid_value(self, param_value, param_name, env_variable, error_trace):
        if param_value is None:
            error_trace.AddError(
                core.FireError(self.__validation_error_msg.format(param=param_name, env_variable=env_variable)),
                sys.argv[1:])
        if param_value and param_name == 'url':
            self.__is_valid_url(param_value, error_trace)

    def __is_valid_url(self, url_value, error_trace):
        try:
            result = urlparse(url_value)
            if not all([result.scheme, result.netloc]):  # URL scheme specifier and Network location part are mandatory
                error_trace.AddError(core.FireError(self.__validation_url_malformated_error_msg.format(url=url_value)),
                                     sys.argv[1:])
            else:
                try:
                    # if no port given in url, send http over port 80 and https over port 443, fallback to 4516
                    port = result.port if result.port else 443 if result.scheme == 'https' else 80 if result.scheme == 'http' else 4516
                    portNumber = int(port)
                    if portNumber < 0:
                        error_trace.AddError(core.FireError(
                            self.__validation_url_invalid_port_msg.format(url=url_value)), sys.argv[1:])
                except:
                    error_trace.AddError(core.FireError(self.__validation_url_invalid_port_msg.format(url=url_value)),
                                         sys.argv[1:])
        except:
            error_trace.AddError(core.FireError(self.__validation_url_parse_error_msg.format(url=url_value)),
                                 sys.argv[1:])

    def __print_validation_errors(self, error_trace):
        error_message = 'Usage Error: \n' + '\n'.join(
            '{index}. {trace_string}'.format(index=index + 1, trace_string=element)
            for index, element in enumerate(error_trace.elements[1:]))
        print(error_message, file=sys.stderr)
