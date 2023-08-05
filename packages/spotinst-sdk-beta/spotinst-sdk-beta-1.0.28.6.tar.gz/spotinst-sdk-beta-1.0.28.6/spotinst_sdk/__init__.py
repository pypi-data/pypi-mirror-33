import json
import os
import re

import requests
import yaml

from spotinst_sdk import aws_elastigroup
from spotinst_sdk import spotinst_functions

CREDENTIALS_FILE = os.path.join(os.path.expanduser("~"), '.spotinst', 'credentials')

__version__ = '1.0.28.6'
_SpotinstClient__spotinst_sdk_python_agent_name = 'spotinst-sdk-python'
_SpotinstClient__spotinst_sdk_user_agent = '{}/{}'.format(_SpotinstClient__spotinst_sdk_python_agent_name, __version__)


class SpotinstClient:
    __account_id_key = "accountId"
    __base_elastigroup_url = "https://api.spotinst.io/aws/ec2/group"
    __base_functions_url = "https://api.spotinst.io/functions"
    camel_pat = re.compile(r'([A-Z])')
    under_pat = re.compile(r'_([a-z])')

    # region Constructor
    def __init__(self, auth_token=None,
                 account_id=None,
                 profile='default',
                 print_output=True,
                 user_agent=None):
        """

        :type auth_token: str
        :type account_id: str
        :type profile: str
        :type print_output: bool
        :type user_agent: str
        """
        self.auth_token = auth_token
        self.account_id = account_id

        if not auth_token or not account_id:
            self.load_credentials(profile=profile)

        self.should_print_output = print_output
        self.user_agent = user_agent

    # endregion

    # region Elastigroup
    def create_elastigroup(self, group):

        group = aws_elastigroup.ElastigroupCreationRequest(group)

        excluded_group_dict = self.exclude_missing(json.loads(group.toJSON()))

        formatted_group_dict = self.convert_json(excluded_group_dict, self.underscore_to_camel)

        body_json = json.dumps(formatted_group_dict)

        self.print_output(body_json)

        group_response = self.send_post(body_json, self.__base_elastigroup_url, entity_name='elastigroup')

        formatted_response = self.convert_json(group_response, self.camel_to_underscore)

        retVal = formatted_response["response"]["items"][0]

        return retVal

    def scale_elastigroup_up(self, group_id, adjustment):
        query_params = dict({"adjustment": adjustment})
        content = self.send_put_with_params(url=self.__base_elastigroup_url + "/" + str(group_id) + "/scale/up",
                                            entity_name='elastigroup (scale up)',
                                            body=None,
                                            user_query_params=query_params)

        formatted_response = self.convert_json(content, self.camel_to_underscore)
        return formatted_response["response"]["items"]

    def scale_elastigroup_down(self, group_id, adjustment):
        query_params = dict({"adjustment": adjustment})
        content = self.send_put_with_params(url=self.__base_elastigroup_url + "/" + str(group_id) + "/scale/down",
                                            entity_name='elastigroup (scale down)',
                                            body=None,
                                            user_query_params=query_params)

        formatted_response = self.convert_json(content, self.camel_to_underscore)
        return formatted_response["response"]["items"]

    def update_elastigroup(self, group_update, group_id):

        group = aws_elastigroup.ElastigroupUpdateRequest(group_update)

        excluded_group_update_dict = self.exclude_missing(json.loads(group.toJSON()))

        formatted_group_update_dict = self.convert_json(excluded_group_update_dict, self.underscore_to_camel)

        body_json = json.dumps(formatted_group_update_dict)

        self.print_output(body_json)

        group_response = self.send_put(body_json, self.__base_elastigroup_url + "/" + group_id,
                                       entity_name='elastigroup')

        formatted_response = self.convert_json(group_response, self.camel_to_underscore)

        retVal = formatted_response["response"]["items"][0]

        return retVal

    def delete_elastigroup(self, group_id):
        delurl = self.__base_elastigroup_url + "/" + group_id
        response = self.send_delete(url=delurl, entity_name='elastigroup')
        return response

    def delete_elastigroup_with_deallocation(self, group_id, stateful_deallocation):
        delurl = self.__base_elastigroup_url + "/" + group_id

        deletion_request = aws_elastigroup.ElastigroupDeletionRequest(stateful_deallocation)

        excluded_deletion_dict = self.exclude_missing(json.loads(deletion_request.toJSON()))
        formatted_deletion_dict = self.convert_json(excluded_deletion_dict, self.underscore_to_camel)
        body_json = json.dumps(formatted_deletion_dict)

        response = self.send_delete_with_body(body=body_json, url=delurl, entity_name='elastigroup')

        return response

    def get_elastigroup(self, group_id):
        geturl = self.__base_elastigroup_url + "/" + group_id
        result = self.send_get(url=geturl, entity_name='elastigroup')

        formatted_response = self.convert_json(result, self.camel_to_underscore)

        return formatted_response["response"]["items"][0]

    def get_elastigroups(self):
        content = self.send_get(url=self.__base_elastigroup_url, entity_name='elastigroup')
        formatted_response = self.convert_json(content, self.camel_to_underscore)
        return formatted_response["response"]["items"]

    def get_elastigroup_active_instances(self, group_id):
        content = self.send_get(url=self.__base_elastigroup_url + "/" + str(group_id) + "/status",
                                entity_name='active instances')
        formatted_response = self.convert_json(content, self.camel_to_underscore)
        return formatted_response["response"]["items"]

    def roll_group(self, group_id, group_roll):

        group_roll_request = aws_elastigroup.ElastigroupRollRequest(group_roll=group_roll)

        excluded_group_roll_dict = self.exclude_missing(json.loads(group_roll_request.toJSON()))

        formatted_group_roll_dict = self.convert_json(excluded_group_roll_dict, self.underscore_to_camel)

        body_json = json.dumps(formatted_group_roll_dict)

        self.print_output(body_json)

        roll_response = self.send_put(url=self.__base_elastigroup_url + "/" + str(group_id) + "/roll",
                                      body=body_json, entity_name='roll')

        formatted_response = self.convert_json(roll_response, self.camel_to_underscore)

        retVal = formatted_response["response"]["items"]

        return retVal

    def detach_elastigroup_instances(self, group_id, detach_configuration):

        group_detach_request = aws_elastigroup.ElastigroupDetachInstancesRequest(
            detach_configuration=detach_configuration)

        excluded_group_detach_dict = self.exclude_missing(json.loads(group_detach_request.toJSON()))

        formatted_group_detach_dict = self.convert_json(excluded_group_detach_dict, self.underscore_to_camel)

        body_json = json.dumps(formatted_group_detach_dict)

        self.print_output(body_json)

        detach_response = self.send_put(url=self.__base_elastigroup_url + "/" + str(group_id) + "/detachInstances",
                                        body=body_json, entity_name='detach')

        formatted_response = self.convert_json(detach_response, self.camel_to_underscore)

        retVal = formatted_response["response"]["status"]

        return retVal

    # endregion

    # region Functions
    def create_application(self, app):

        app = spotinst_functions.ApplicationCreationRequest(app)

        excluded_group_dict = self.exclude_missing(json.loads(app.toJSON()))

        formatted_app_dict = self.convert_json(excluded_group_dict, self.underscore_to_camel)

        body_json = json.dumps(formatted_app_dict)

        self.print_output(body_json)

        app_response = self.send_post(body_json, self.__base_functions_url + '/application', entity_name='application')

        formatted_response = self.convert_json(app_response, self.camel_to_underscore)

        retVal = formatted_response["response"]["items"][0]

        return retVal

    def create_environment(self, env):

        env = spotinst_functions.EnvironmentCreationRequest(env)

        excluded_env_dict = self.exclude_missing(json.loads(env.toJSON()))

        formatted_env_dict = self.convert_json(excluded_env_dict, self.underscore_to_camel)

        body_json = json.dumps(formatted_env_dict)

        self.print_output(body_json)

        env_response = self.send_post(body_json, self.__base_functions_url + '/environment', entity_name='environment')

        formatted_response = self.convert_json(env_response, self.camel_to_underscore)

        retVal = formatted_response["response"]["items"][0]

        return retVal

    def create_function(self, fx):

        fx = spotinst_functions.FunctionCreationRequest(fx, self.should_print_output)

        excluded_fx_dict = self.exclude_missing(json.loads(fx.toJSON()))

        formatted_fx_dict = self.convert_json(excluded_fx_dict, self.underscore_to_camel)

        body_json = json.dumps(formatted_fx_dict)

        formatted_fx_dict['function']['code']['source'] = 'INLINE_BASE64_SOURCE_CODE'
        self.print_output(json.dumps(formatted_fx_dict))

        fx_response = self.send_post(body_json, self.__base_functions_url + '/function', entity_name='function')

        formatted_response = self.convert_json(fx_response, self.camel_to_underscore)

        retVal = formatted_response["response"]["items"][0]

        return retVal

    # endregion

    # region Utils
    def print_output(self, output):
        if self.should_print_output is True:
            print(output)

    def send_get(self, url, entity_name):
        agent = self.resolve_user_agent()
        query_params = self.build_query_params()
        headers = dict(
            {
                'User-Agent': agent,
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.auth_token
            }
        )

        self.print_output("Sending get request to spotinst API.")
        result = requests.get(url, params=query_params, headers=headers)

        if result.status_code == self.HTTP_STATUS_CODES.SUCCESS:
            self.print_output("Success")
            data = json.loads(result.content)
            return data
        else:
            self.handle_exception("getting {}".format(entity_name), result)

    def send_delete(self, url, entity_name):
        agent = self.resolve_user_agent()
        query_params = self.build_query_params()
        headers = dict(
            {
                'User-Agent': agent,
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.auth_token
            }
        )

        self.print_output("Sending deletion request to spotinst API.")
        result = requests.delete(url, params=query_params, headers=headers)

        if result.status_code == self.HTTP_STATUS_CODES.SUCCESS:
            self.print_output("Success")
            return True
        else:
            self.handle_exception("deleting {}".format(entity_name), result)

    def send_delete_with_body(self, body, url, entity_name):
        agent = self.resolve_user_agent()
        query_params = self.build_query_params()
        headers = dict(
            {
                'User-Agent': agent,
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.auth_token
            }
        )

        self.print_output("Sending deletion request to spotinst API.")
        result = requests.delete(url, params=query_params, headers=headers, data=body)

        if result.status_code == self.HTTP_STATUS_CODES.SUCCESS:
            self.print_output("Success")
            return True
        else:
            self.handle_exception("deleting {}".format(entity_name), result)

    def send_post(self, body, url, entity_name):
        agent = self.resolve_user_agent()
        query_params = self.build_query_params()
        headers = dict(
            {
                'User-Agent': agent,
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.auth_token
            }
        )

        self.print_output("Sending post request to spotinst API.")
        result = requests.post(url, params=query_params, data=body, headers=headers)

        if result.status_code == self.HTTP_STATUS_CODES.SUCCESS:
            self.print_output("Success")
            data = json.loads(result.content)
            return data
        else:
            self.handle_exception("creating {}".format(entity_name), result)

    def send_put(self, body, url, entity_name):
        agent = self.resolve_user_agent()
        query_params = self.build_query_params()
        headers = dict(
            {
                'User-Agent': agent,
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.auth_token
            }
        )

        self.print_output("Sending put request to spotinst API.")
        result = requests.put(url, params=query_params, data=body, headers=headers)

        if result.status_code == self.HTTP_STATUS_CODES.SUCCESS:
            self.print_output("Success")
            data = json.loads(result.content)
            return data
        else:
            self.handle_exception("updating {}".format(entity_name), result)

    def send_put_with_params(self, body, url, entity_name, user_query_params):
        agent = self.resolve_user_agent()
        query_params = self.build_query_params_with_input(user_query_params)

        headers = dict(
            {
                'User-Agent': agent,
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.auth_token
            }
        )

        self.print_output("Sending put request to spotinst API.")
        result = requests.put(url, params=query_params, data=body, headers=headers)

        if result.status_code == self.HTTP_STATUS_CODES.SUCCESS:
            self.print_output("Success")
            data = json.loads(result.content)
            return data
        else:
            self.handle_exception("updating {}".format(entity_name), result)

    def resolve_user_agent(self):
        global _SpotinstClient__spotinst_sdk_user_agent
        agent = _SpotinstClient__spotinst_sdk_user_agent
        if self.user_agent is not None:
            agent = '{}+{}'.format(self.user_agent, agent)
        return agent

    def handle_exception(self, action_string, result):
        self.print_output(result.status_code)
        data = json.loads(result.content)
        response_json = json.dumps(data["response"])
        self.print_output(response_json)
        raise SpotinstClientException("Error encountered while " + action_string, response_json)

    def convert_json(self, val, convert):
        new_json = {}
        if val is None:
            return val
        elif type(val) in (int, float, bool, "".__class__, u"".__class__):
            return val
        for k, v in list(val.items()):
            new_v = v
            if isinstance(v, dict):
                new_v = self.convert_json(v, convert)
            elif isinstance(v, list):
                new_v = list()
                for x in v:
                    new_v.append(self.convert_json(x, convert))
            new_json[convert(k)] = new_v
        return new_json

    def exclude_missing(self, obj):
        # Delete keys with the value 'none' in a dictionary, recursively.

        # if obj.items() is not None:
        if obj.items() is not None:
            for key, value in list(obj.items()):

                # Remove none values
                if value == aws_elastigroup.none:
                    del obj[key]

                # Handle Objects
                elif isinstance(value, dict):
                    self.exclude_missing(obj=value)

                # Handle lists
                elif self.is_sequence(arg=value):
                    for listitem in value:
                        # Handle Lists of objects
                        try:
                            self.exclude_missing(obj=listitem)
                        except AttributeError:
                            pass
        return obj  # For convenience

    def is_sequence(self, arg):
        return (not hasattr(arg, "strip") and
                hasattr(arg, "__getitem__") or
                hasattr(arg, "__iter__"))

    def build_query_params(self):
        query_params = None
        if self.account_id is not None:
            query_params = dict({self.__account_id_key: self.account_id})

        return query_params

    def build_query_params_with_input(self, user_params):
        query_params = dict()
        if self.account_id is not None:
            query_params = dict({self.__account_id_key: self.account_id})

        if user_params is not None:
            query_params = self.merge_two_dicts(query_params, user_params)

        return query_params

    @staticmethod
    def merge_two_dicts(x, y):
        z = x.copy()  # start with x's keys and values
        z.update(y)  # modifies z with y's keys and values & returns None
        return z

    def camel_to_underscore(self, name):
        return self.camel_pat.sub(lambda x: '_' + x.group(1).lower(), name)

    def underscore_to_camel(self, name):
        return self.under_pat.sub(lambda x: x.group(1).upper(), name)

    def load_credentials(self, profile):
        self.account_id = os.environ.get('SPOTINST_ACCOUNT', None)
        self.auth_token = os.environ.get('SPOTINST_TOKEN', None)

        if not self.account_id or not self.auth_token:
            with open(CREDENTIALS_FILE, 'r') as credentials_file:
                config = yaml.load(credentials_file)

                if config:
                    self.account_id = config.get(profile, {}).get("account", None)
                    self.auth_token = config.get(profile, {}).get("token", None)

                if not self.account_id or not self.auth_token:
                    raise SpotinstClientException("failed to load credentials")

    # endregion

    class HTTP_STATUS_CODES:
        SUCCESS = 200
        BAD_REQUEST = 400
        UNAUTHORIZED = 401
        INTERNAL_SERVER_ERROR = 500


class SpotinstClientException(Exception):
    def __init__(self, message, response):
        message = message + "\n" + response
        # Call the base class constructor with the parameters it needs
        super(SpotinstClientException, self).__init__(message)
