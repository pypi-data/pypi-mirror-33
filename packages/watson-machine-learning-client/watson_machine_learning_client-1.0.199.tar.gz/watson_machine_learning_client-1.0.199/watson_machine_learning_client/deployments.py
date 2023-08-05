################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################

from __future__ import print_function
import requests
import json
from watson_machine_learning_client.utils import DEPLOYMENT_DETAILS_TYPE, INSTANCE_DETAILS_TYPE, print_text_header_h1, print_text_header_h2, STR_TYPE, STR_TYPE_NAME, docstring_parameter, str_type_conv, StatusLogger, convert_metadata_to_parameters, create_download_link, is_ipython
from watson_machine_learning_client.wml_client_error import WMLClientError, MissingValue, ApiRequestFailure
from watson_machine_learning_client.href_definitions import is_uid
from watson_machine_learning_client.wml_resource import WMLResource


class Deployments(WMLResource):
    """
        Deploy and score published models.
    """
    def __init__(self, client):
        WMLResource.__init__(self, __name__, client)
        Deployments._validate_type(client.service_instance.details, u'instance_details', dict, True)
        Deployments._validate_type_of_details(client.service_instance.details, INSTANCE_DETAILS_TYPE)

    def _get_url_for_uid(self, deployment_uid):
        response_get = requests.get(
            self._href_definitions.get_deployments_href(),
            headers=self._client._get_headers())

        try:
            if response_get.status_code == 200:
                for el in response_get.json().get(u'resources'):
                    if el.get(u'metadata').get(u'guid') == deployment_uid:
                        return el.get(u'metadata').get('url')
            else:
                raise ApiRequestFailure(u'Couldn\'t generate url from uid: \'{}\'.'.format(deployment_uid), response_get)
        except Exception as e:
            raise WMLClientError(u'Failed during getting url for uid: \'{}\'.'.format(deployment_uid), e)

        raise WMLClientError(u'No matching url for uid: \'{}\'.'.format(deployment_uid))

    def update(self, deployment_uid, name=None, description=None, asynchronous=False, meta_props=None):
        """
            Update model used in deployment to the latest version. The scoring_url remains.
            Name and description change will not work for online deployment.
            For virtual deployments the file will be updated under the same download_url.

            :param deployment_uid:  Deployment UID
            :type deployment_uid: str

            :param name: new name for deployment
            :type name: str

            :param description: new description for deployment
            :type description: str

            :param meta_props: dictionary with parameters used for virtual deployment (Core ML format)
            :type meta_props: dict

            :returns: updated metadata of deployment
            :rtype: dict

            A way you might use me is:

            >>> deployment_details = client.deployments.update(deployment_uid)
            >>> deployment_details = client.deployments.update(deployment_uid, meta_props_names=new_CoreML_parameters)
        """
        deployment_uid = str_type_conv(deployment_uid)
        Deployments._validate_type(deployment_uid, 'deployment_uid', STR_TYPE, True)

        deployment_details = self.get_details(deployment_uid)
        model_uid = self._get_required_element_from_dict(deployment_details, 'deployment_details', ['entity', 'published_model', 'guid'])

        if name is not None or description is not None:
            meta_props_names = {
                "name": name,
                "description": description
            }

            meta_props_data = []

            if name is not None:
                meta_props_data.append({"name": "name", "type": STR_TYPE, "path": ["name"]})

            if description is not None:
                meta_props_data.append({"name": "description", "type": STR_TYPE, "path": ["description"]})

            url = self._href_definitions.get_deployment_href(model_uid, deployment_uid)
            self._update(url, deployment_details, meta_props_names, meta_props_data)

        deployment_type = str(self._get_required_element_from_dict(deployment_details, 'deployment_details', ['entity', 'type'])).lower()

        if 'virtual' in deployment_type:
            deployment_format = str(self._get_required_element_from_dict(deployment_details, 'deployment_details', ['entity', 'format'])).lower()

            response = requests.patch(
                self._href_definitions.get_deployment_href(model_uid, deployment_uid),
                headers=self._client._get_headers(),
                json=[
                    {
                        "op": "replace",
                        "path": "/parameters",
                        "value": convert_metadata_to_parameters(meta_props)
                    }
                ]
            )

            self._handle_response(200, 'updating Core ML version in virtual deployment', response, False)
        else:
            model_details = self._client.repository.get_model_details(model_uid)
            print('model_details', model_details)
            latest_version_url = self._get_required_element_from_dict(model_details, 'model_details', ['entity', 'latest_version', 'url'])

            response = requests.patch(
                self._href_definitions.get_published_model_href(model_uid),
                headers=self._client._get_headers(),
                json=[
                    {
                        "op": "replace",
                        "path": "/deployed_version/url",
                        "value": latest_version_url
                    }
                ]
            )

            self._handle_response(200, 'updating model version in deployment', response, False)

        if not asynchronous:
            if response.status_code == 200:
                deployment_details = response.json()
                deployment_uid = self.get_uid(deployment_details)

                import time
                print_text_header_h1(u'Synchronous deployment update for uid: \'{}\' started'.format(model_uid))

                status = deployment_details[u'entity'][u'status']

                with StatusLogger(status) as status_logger:
                    while True:
                        time.sleep(5)
                        deployment_details = self._client.deployments.get_details(deployment_uid)
                        status = deployment_details[u'entity'][u'status']
                        status_logger.log_state(status)

                        if status != u'DEPLOY_IN_PROGRESS':
                            break

                if status == u'DEPLOY_SUCCESS':
                    print(u'')
                    print_text_header_h2(
                        u'Successfully finished deployment update, deployment_uid=\'{}\''.format(deployment_uid))
                    return deployment_details
                else:
                    print_text_header_h2(u'Deployment update failed')
                    try:
                        if 'status_details' in deployment_details[u'entity']:
                            for error in deployment_details[u'entity'][u'status_details'][u'failure'][u'errors']:
                                error_obj = json.loads(error)
                                print(error_obj[u'message'])

                            raise WMLClientError(
                                u'Deployment update failed. Errors: ' + str(
                                    deployment_details[u'entity'][u'status_details'][u'failure'][
                                        u'errors']))
                        else:
                            print(deployment_details[u'entity'][u'status_message'])
                            raise WMLClientError(
                                u'Deployment update failed. Error: ' + str(
                                    deployment_details[u'entity'][u'status_message']
                                ))
                    except WMLClientError as e:
                        raise e
                    except Exception as e:
                        self._logger.debug(u'Deployment update failed:', e)
                        raise WMLClientError(u'Deployment update failed.')

            else:
                error_msg = u'Deployment update failed'
                reason = response.text
                print(reason)
                print_text_header_h2(error_msg)
                raise WMLClientError(error_msg + u'. Error: ' + str(response.status_code) + '. ' + reason)

        return self.get_details()

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_details(self, deployment_uid=None):
        """
           Get information about your deployment(s).

           :param deployment_uid:  Deployment UID (optional)
           :type deployment_uid: {str_type}

           :returns: metadata of deployment(s)
           :rtype: dict

           A way you might use me is:

            >>> deployment_details = client.deployments.get_details(deployment_uid)
            >>> deployment_details = client.deployments.get_details(deployment_uid=deployment_uid)
            >>> deployments_details = client.deployments.get_details()
        """
        deployment_uid = str_type_conv(deployment_uid)
        Deployments._validate_type(deployment_uid, u'deployment_uid', STR_TYPE, False)

        if deployment_uid is not None and not is_uid(deployment_uid):
            raise WMLClientError(u'\'deployment_uid\' is not an uid: \'{}\''.format(deployment_uid))

        if deployment_uid is not None:
            deployment_url = self._get_url_for_uid(deployment_uid)
        else:
            deployment_url = self._client.service_instance.details.get(u'entity').get(u'deployments').get(u'url')

        response_get = requests.get(
            deployment_url,
            headers=self._client._get_headers())

        return self._handle_response(200, u'getting deployment(s) details', response_get)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_status(self, deployment_uid):
        """
            Get status of deployment creation.

            :param deployment_uid: Guid of deployment
            :type deployment_uid: {str_type}

            :returns: status of deployment creation
            :rtype: {str_type}

            A way you might use me is:

             >>> status = client.deployments.get_status(deployment_uid)
        """
        deployment_uid = str_type_conv(deployment_uid)
        Deployments._validate_type(deployment_uid, u'deployment_uid', STR_TYPE, True)

        details = self.get_details(deployment_uid)
        return self._get_required_element_from_dict(details, u'deployment_details', [u'entity', u'status'])

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def create(self, model_uid, name=u'Model deployment', description=u'Description of deployment', asynchronous=False, deployment_type=u'online', deployment_format='Core ML', meta_props=None):
        """
            Create model deployment (online).

            :param model_uid:  Published model UID
            :type model_uid: {str_type}
            :param name: Deployment name
            :type name: {str_type}
            :param description: Deployment description
            :type description: {str_type}
            :param asynchronous: if `False` then will wait until deployment will be fully created before returning
            :type asynchronous: bool
            :param deployment_type: type of deployment ('online', 'virtual'). Default one is 'online'
            :type deployment_type: {str_type}
            :param deployment_format: file format of virtual deployment. Currently supported is 'Core ML' only (default value)
            :type deployment_format: {str_type}
            :param meta_props: dictionary with parameters used for virtual deployment (Core ML format)
            :type meta_props: dict

            :returns: details of created deployment
            :rtype: dict

            A way you might use me is:

             >>> online_deployment = client.deployments.create(model_uid, 'Deployment X', 'Online deployment of XYZ model.')
             >>> virtual_deployment = client.deployments.create(model_uid, 'Deployment A', 'Virtual deployment of XYZ model.', deployment_type='virtual')
         """
        model_uid = str_type_conv(model_uid)
        Deployments._validate_type(model_uid, u'model_uid', STR_TYPE, True)
        name = str_type_conv(name)
        Deployments._validate_type(name, u'name', STR_TYPE, True)
        description = str_type_conv(description)
        Deployments._validate_type(description, u'description', STR_TYPE, True)

        if 'online'.lower() in str(deployment_type).lower():
            response = self._create_online(model_uid=model_uid, name=name, description=description)
        elif 'virtual'.lower() in str(deployment_type).lower() and ('Core ML'.lower() in str(deployment_format).lower()):
            response = self._create_virtual(model_uid=model_uid, name=name, description=description, deployment_format=deployment_format, meta_props=meta_props)
        else:
            raise WMLClientError(u'Deployment creation failed. Unsupported deployment type/format:' + str(deployment_type) + u'/' + str(deployment_format))

        if asynchronous:
            if response.status_code == 202:
                deployment_details = response.json()
                deployment_uid = self.get_uid(deployment_details)
                print_text_header_h1(u'Asynchronous deployment creation for uid: \'{}\' started'.format(model_uid))
                print(u'To monitor status of your deployment use: client.deployments.get_status(\"{}\")'.format(deployment_uid))
                print(u'Scoring url for this deployment: \"{}\"'.format(self.get_scoring_url(deployment_details)))
                return deployment_details
            else:
                return self._handle_response(201, u'deployment creation', response)
        else:
            if response.status_code == 202:
                deployment_details = response.json()
                deployment_uid = self.get_uid(deployment_details)

                import time
                print_text_header_h1(u'Synchronous deployment creation for uid: \'{}\' started'.format(model_uid))

                status = deployment_details[u'entity'][u'status']

                with StatusLogger(status) as status_logger:
                    while True:
                        time.sleep(5)
                        deployment_details = self._client.deployments.get_details(deployment_uid)
                        status = deployment_details[u'entity'][u'status']
                        status_logger.log_state(status)

                        if status != u'DEPLOY_IN_PROGRESS':
                            break

                if status == u'DEPLOY_SUCCESS':
                    print(u'')
                    print_text_header_h2(u'Successfully finished deployment creation, deployment_uid=\'{}\''.format(deployment_uid))
                    return deployment_details
                else:
                    print_text_header_h2(u'Deployment creation failed')
                    try:
                        for error in deployment_details[u'entity'][u'status_details'][u'failure'][u'errors']:
                            if type(error) == str:
                                try:
                                    error_obj = json.loads(error)
                                    print(error_obj[u'message'])
                                except:
                                    print(error)
                            elif type(error) == dict:
                                print(error['message'])
                            else:
                                print(error)

                        raise WMLClientError(
                            u'Deployment creation failed. Errors: ' + str(deployment_details[u'entity'][u'status_details'][u'failure'][
                                u'errors']))
                    except WMLClientError as e:
                        raise e
                    except Exception as e:
                        self._logger.debug(u'Deployment creation failed:', e)
                        raise WMLClientError(u'Deployment creation failed.')
            elif response.status_code == 201:
                deployment_details = response.json()
                deployment_uid = self.get_uid(deployment_details)
                print_text_header_h1(u'Synchronous deployment creation for uid: \'{}\' started'.format(model_uid))
                print(u'DEPLOY_SUCCESS')
                print_text_header_h2(u'Successfully finished deployment creation, deployment_uid=\'{}\''.format(deployment_uid))
                return deployment_details
            elif response.status_code == 303:
                deployment_details = response.json()
                deployment_uid = self.get_uid(deployment_details)
                print_text_header_h2(
                    u'Deployment already exists, deployment_uid=\'{}\''.format(deployment_uid))
                return deployment_details
            elif response.status_code == 200:
                # TODO it should be 303 but 200 is returned ... this elif should be removed when 303
                deployment_details = response.json()
                deployment_uid = self.get_uid(deployment_details)
                print_text_header_h2(
                    u'Deployment already exists, deployment_uid=\'{}\''.format(deployment_uid))
                return deployment_details
            else:
                error_msg = u'Deployment creation failed'
                reason = response.text
                print(reason)
                print_text_header_h2(error_msg)
                raise WMLClientError(error_msg + u'. Error: ' + str(response.status_code) + '. ' + reason)

    def _create_online(self, model_uid, name, description):
        """
            Create online deployment.
        """
        url = self._client.service_instance.details.get(u'entity').get(u'published_models').get(
            u'url') + u'/' + model_uid + u'/' + u'deployments?sync=false'

        response = requests.post(
            url,
            json={u'name': name, u'description': description, u'type': u'online'},
            headers=self._client._get_headers())

        return response

    def _create_virtual(self, model_uid, name='Virtual deployment', description='Virtual deployment description', deployment_format='Core ML', meta_props=None):
        """
            Creates virtual deployment.
        """

        url = self._client.service_instance.details.get(u'entity').get(u'published_models').get(
            u'url') + u'/' + model_uid + u'/' + u'deployments?sync=false'

        response = requests.post(
            url,
            json={u'name': name, u'description': description, u'type': u'virtual', u'format': deployment_format, u'parameters': convert_metadata_to_parameters(meta_props)},
            headers=self._client._get_headers())

        return response

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_scoring_url(deployment):
        """
            Get scoring_url from deployment details.

            :param deployment: Created deployment details
            :type deployment: dict

            :returns: scoring endpoint URL that is used for making scoring requests
            :rtype: {str_type}

            A way you might use me is:

             >>> scoring_url = client.deployments.get_scoring_url(deployment)
        """
        Deployments._validate_type(deployment, u'deployment', dict, True)
        Deployments._validate_type_of_details(deployment, DEPLOYMENT_DETAILS_TYPE)

        try:
            url = deployment.get(u'entity').get(u'scoring_url')
        except Exception as e:
            raise WMLClientError(u'Getting scoring url for deployment failed.', e)

        if url is None:
            raise MissingValue(u'entity.scoring_url')

        return url

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_uid(deployment_details):
        """
            Get deployment_uid from deployment details.

            :param deployment_details: Created deployment details
            :type deployment_details: dict

            :returns: deployment UID that is used to manage the deployment
            :rtype: {str_type}

            A way you might use me is:

            >>> deployment_uid = client.deployments.get_uid(deployment)
        """
        Deployments._validate_type(deployment_details, u'deployment_details', dict, True)
        Deployments._validate_type_of_details(deployment_details, DEPLOYMENT_DETAILS_TYPE)

        try:
            uid = deployment_details.get(u'metadata').get(u'guid')
        except Exception as e:
            raise WMLClientError(u'Getting deployment uid from deployment details failed.', e)

        if uid is None:
            raise MissingValue(u'deployment_details.metadata.guid')

        return uid

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_url(deployment_details):
        """
            Get deployment_url from deployment details.

            :param deployment_details:  Created deployment details
            :type deployment_details: dict

            :returns: deployment URL that is used to manage the deployment
            :rtype: {str_type}

            A way you might use me is:

            >>> deployment_url = client.deployments.get_url(deployment)
        """
        Deployments._validate_type(deployment_details, u'deployment_details', dict, True)
        Deployments._validate_type_of_details(deployment_details, DEPLOYMENT_DETAILS_TYPE)

        try:
            url = deployment_details.get(u'metadata').get(u'url')
        except Exception as e:
            raise WMLClientError(u'Getting deployment url from deployment details failed.', e)

        if url is None:
            raise MissingValue(u'deployment_details.metadata.url')

        return url

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_download_url(deployment_details):
        """
            Get deployment_download_url from deployment details.

            :param deployment_details:  Created deployment details
            :type deployment_details: dict

            :returns: deployment download URL that is used to get file deployment (for example: Core ML)
            :rtype: {str_type}

            A way you might use me is:

            >>> deployment_url = client.deployments.get_download_url(deployment)
        """
        Deployments._validate_type(deployment_details, u'deployment_details', dict, True)
        Deployments._validate_type_of_details(deployment_details, DEPLOYMENT_DETAILS_TYPE)

        try:
            url = deployment_details.get(u'entity').get(u'download_details').get(u'url')
        except Exception as e:
            raise WMLClientError(u'Getting download url from deployment details failed.', e)

        if url is None:
            raise MissingValue(u'deployment_details.entity.download_details.url')

        return url

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def delete(self, deployment_uid):
        """
            Delete model deployment.

            :param deployment_uid: Deployment UID
            :type deployment_uid: {str_type}

            A way you might use me is:

            >>> client.deployments.delete(deployment_uid)
        """
        deployment_uid = str_type_conv(deployment_uid)
        Deployments._validate_type(deployment_uid, u'deployment_uid', STR_TYPE, True)

        if deployment_uid is not None and not is_uid(deployment_uid):
            raise WMLClientError(u'\'deployment_uid\' is not an uid: \'{}\''.format(deployment_uid))

        deployment_url = self._get_url_for_uid(deployment_uid)

        response_delete = requests.delete(
            deployment_url,
            headers=self._client._get_headers())

        self._handle_response(204, u'deployment deletion', response_delete, False)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def score(self, scoring_url, payload):
        """
            Make scoring requests against deployed model.

            :param scoring_url:  scoring endpoint URL
            :type scoring_url: {str_type}
            :param payload: records to score
            :type payload: dict

            :returns: scoring result containing prediction and probability
            :rtype: dict

            A way you might use me is:

            >>> scoring_payload = {'fields': ['GENDER','AGE','MARITAL_STATUS','PROFESSION'], 'values': [['M',23,'Single','Student'],['M',55,'Single','Executive']]}
            >>> predictions = client.deployments.score(scoring_url, scoring_payload)
        """
        scoring_url = str_type_conv(scoring_url)
        Deployments._validate_type(scoring_url, u'scoring_url', STR_TYPE, True)
        Deployments._validate_type(payload, u'payload', dict, True)

        response_scoring = requests.post(
            scoring_url,
            json=payload,
            headers=self._client._get_headers())

        return self._handle_response(200, u'scoring', response_scoring)

    def list(self):
        """
           List deployments.

           A way you might use me is:

           >>> client.deployments.list()
        """
        from tabulate import tabulate

        details = self.get_details()
        resources = details[u'resources']
        values = [(m[u'metadata'][u'guid'], m[u'entity'][u'name'], m[u'entity'][u'type'], m[u'entity'][u'status'], m[u'metadata'][u'created_at'], m[u'entity'][u'model_type']) for m in resources]
        table = tabulate([[u'GUID', u'NAME', u'TYPE', u'STATE', u'CREATED', u'FRAMEWORK']] + values)
        print(table)

    def get_uids(self):
        """
            Get all deployments uids.

            :returns: list of uids
            :rtype: list of strings

            A way you might use me is:

            >>> deployments_uids = client.deployments.get_uids()
        """
        details = self.get_details()
        resources = details[u'resources']
        uids = []

        for x in resources:
            uids.append(x['metadata']['guid'])

        return uids

    """
    def _create_virtual(self, model_uid, deployment_format='Core ML', meta_props=None):


        # TODO to be replaced with deployment service call (REST API)

        from watson_machine_learning_client.tools.model_converter import ModelConverter

        converter = ModelConverter(
            self._wml_credentials['url'],
            self._wml_credentials['instance_id'],
            self._client.wml_token
        )
        print_text_header_h1("Creating virtual deployment for model: " + model_uid)

        try:
            filepath = converter.run(model_uid=model_uid, file_format=deployment_format, meta_props=meta_props)
            print_text_header_h2("Virtual deployment created: " + filepath)
            return filepath
        except Exception as e:
            raise WMLClientError(u'Conversion to Core ML format failed.', e)
    """

    def download(self, virtual_deployment_uid, filename=None):
        """
            Downloads file deployment of specified UID. Currently supported format is Core ML.

            :param virtual_deployment_uid:  UID of virtual deployment
            :type virtual_deployment_uid: {str_type}
            :param filename: filename of downloaded archive (optional)
            :type filename: {str_type}

            :returns: path to downloaded file or creates download link (iPython)
            :rtype: {str_type}
        """

        virtual_deployment_uid = str_type_conv(virtual_deployment_uid)
        Deployments._validate_type(virtual_deployment_uid, u'deployment_uid', STR_TYPE, False)

        if virtual_deployment_uid is not None and not is_uid(virtual_deployment_uid):
            raise WMLClientError(u'\'deployment_uid\' is not an uid: \'{}\''.format(virtual_deployment_uid))

        details = self.get_details(virtual_deployment_uid)
        download_url = self.get_download_url(details)

        response_get = requests.get(
            download_url,
            headers=self._client._get_headers())

        if filename is None:
            filename = 'mlmodel.tar.gz'

        if response_get.status_code == 200:
            with open(filename, "wb") as new_file:
                new_file.write(response_get.content)
                new_file.close()

                print_text_header_h2(
                    u'Successfully downloaded deployment file: ' + str(filename))

                return filename
        else:
            raise WMLClientError(u'Unable to download deployment content: ' + response_get.text)
