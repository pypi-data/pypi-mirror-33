################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################

from watson_machine_learning_client.log_util import get_logger
from watson_machine_learning_client.utils import version
from watson_machine_learning_client.learning_system import LearningSystem
from watson_machine_learning_client.experiments import Experiments
from watson_machine_learning_client.repository import Repository
from watson_machine_learning_client.instance import ServiceInstance
from watson_machine_learning_client.deployments import Deployments
from watson_machine_learning_client.training import Training
from watson_machine_learning_client.wml_client_error import NoWMLCredentialsProvided

'''
.. module:: WatsonMachineLearningAPIClient
   :platform: Unix, Windows
   :synopsis: Watson Machine Learning API Client.

.. moduleauthor:: IBM
'''


class WatsonMachineLearningAPIClient:

    def __init__(self, wml_credentials, project_id='Not provided'):
        self._logger = get_logger(__name__)
        if wml_credentials is None:
            raise NoWMLCredentialsProvided()
        self.wml_credentials = wml_credentials
        self.project_id = project_id
        self.wml_token = None
        self.service_instance = ServiceInstance(self)
        self.service_instance.details = self.service_instance.get_details()
        self.repository = Repository(self)
        self.deployments = Deployments(self)
        self.experiments = Experiments(self)
        self.learning_system = LearningSystem(self)
        self.training = Training(self)
        self._logger.info(u'Client successfully initialized')
        self.version = version()

    def _get_headers(self, content_type='application/json', no_content_type=False):
        headers = {
            'Authorization': 'Bearer ' + self.service_instance._get_token(),
            'X-WML-User-Client': 'PythonClient',
            'X-Watson-Project-ID': self.project_id
        }

        if not no_content_type:
            headers.update({'Content-Type': content_type})

        return headers


