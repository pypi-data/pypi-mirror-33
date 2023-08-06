import base64
import json
import io
import logging
import tarfile


class MachineLearningMixin(object):

    def _inject_ml_models(self, config, ml_models, dereference=True):
        if ml_models:
            try:
                with io.BytesIO() as binary_data:
                    with tarfile.open(fileobj=binary_data, mode='w|gz',
                                      dereference=dereference) as tar:
                        tar.add(ml_models, arcname='.', recursive=True)
                    config['ml_models'] =\
                        base64.b64encode(binary_data.getvalue())
            except Exception as e:
                logging.exception(e)
                raise ValueError(e)

    #
    # Machine Learning workflows
    #
    def new_machinelearning_workflow(self, project_id, name, config,
                                     ml_models=None):
        """Create a new Machine Learning Workflow.

        :param project_id: Id of the Squirro project.
        :param name: Name of Machine learning workflow.
        :param config: Dictionary of Machine learning workflow config.
            Detailed documentation here: https://squirro.atlassian.net/wiki/spaces/DOC/pages/337215576/Squirro+Machine+Learning+Documentation  # noqa
        :param ml_models: Directory with ml_models to be uploaded into the workflow
            path
        """

        base_url = '{}/v0/{}/projects/{}/machinelearning_workflows'
        headers = {'Content-Type': 'application/json'}

        url = base_url.format(self.topic_api_url, self.tenant, project_id)

        ml_workflow = {'name': name, 'config': config}

        # Inject token
        ml_workflow['squirro_token'] = self.refresh_token

        # Inject ml_models
        self._inject_ml_models(ml_workflow, ml_models)

        res = self._perform_request(
            'post', url,
            data=json.dumps(ml_workflow), headers=headers)
        return self._process_response(res, [201])

    def get_machinelearning_workflows(self, project_id):
        """Return all Machine Learning workflows for a project.

        :param project_id: Id of the Squirro project.
        """
        base_url = '{}/v0/{}/projects/{}/machinelearning_workflows'
        headers = {'Content-Type': 'application/json'}

        url = base_url.format(self.topic_api_url, self.tenant, project_id)
        res = self._perform_request('get', url, headers=headers)
        return self._process_response(res)

    def get_machinelearning_workflow(self, project_id, ml_workflow_id):
        """Return a specific Machine Learning Workflow in a project.

        :param project_id: Id of the project.
        :param ml_workflow_id: Id of the Machine Learning workflow.
        """
        base_url = '{}/v0/{}/projects/{}/machinelearning_workflows'
        headers = {'Content-Type': 'application/json'}

        url = '/'.join([base_url, ml_workflow_id])
        url = url.format(self.topic_api_url, self.tenant, project_id)
        res = self._perform_request('get', url, headers=headers)
        return self._process_response(res)

    def modify_machinelearning_workflow(self, project_id, ml_workflow_id,
                                        name=None, config=None, ml_models=None):
        """Modify an existing Machine Learning workflow.

        :param project_id: Id of the Squirro project.
        :param ml_workflow_id: Id of the Machine Learning workflow.
        :param name: Name of Machine learning workflow.
        :param config: Dictionary of Machine Learning workflow config.
            Detailed documentation here: https://squirro.atlassian.net/wiki/spaces/DOC/pages/337215576/Squirro+Machine+Learning+Documentation  # noqa
        :param ml_models: Directory with ml_models to be uploaded into the workflow
            path.
        """
        base_url = '{}/v0/{}/projects/{}/machinelearning_workflows'
        headers = {'Content-Type': 'application/json'}

        ml_workflow_update = {}

        # Inject ml_models
        self._inject_ml_models(ml_workflow_update, ml_models)

        # Compose ml_workflow object
        if name is not None:
            ml_workflow_update['name'] = name
        if config is not None:
            ml_workflow_update['config'] = config

        url = '/'.join([base_url, ml_workflow_id])
        url = url.format(self.topic_api_url, self.tenant, project_id)
        res = self._perform_request(
            'put', url, data=json.dumps(ml_workflow_update), headers=headers)
        return self._process_response(res, [204])

    def delete_machinelearning_workflow(self, project_id, ml_workflow_id):
        """Delete a Machine Learning workflow.

        :param project_id: Id of the Squirro project.
        :param ml_workflow_id: Id of the Machine Learning workflow.
        """
        base_url = '{}/v0/{}/projects/{}/machinelearning_workflows'
        headers = {'Content-Type': 'application/json'}

        url = '/'.join([base_url, ml_workflow_id])
        url = url.format(self.topic_api_url, self.tenant, project_id)
        res = self._perform_request('delete', url, headers=headers)
        return self._process_response(res, [204])

    def run_machinelearning_workflow(self, project_id, ml_workflow_id, data):
        """Run a Machine Learning workflow directly on Squirro items.

        :param project_id: Id of the Squirro project.
        :param ml_workflow_id: Id of the Machine Learning workflow.
        :param data: Data to run through Machine Learning workflow.
        """
        base_url = '{}/v0/{}/projects/{}/machinelearning_workflows'
        headers = {'Content-Type': 'application/json'}

        url = '/'.join([base_url, ml_workflow_id])
        url = url.format(self.topic_api_url, self.tenant, project_id)
        res = self._perform_request(
            'post', url, data=json.dumps(data), headers=headers)
        return self._process_response(res)

    #
    # Machine Learning jobs
    #
    def new_machinelearning_job(self, project_id, ml_workflow_id, type):
        """Create a new Machine Learning job.

        :param project_id: Id of the Squirro project.
        :param ml_workflow_id: Id of the Machine learning workflow.
        :param type: Type of the Machine Learning job. Possible values are
            `training` and `inference`.
        """
        base_url = '{}/v0/{}/projects/{}/machinelearning_workflows'
        headers = {'Content-Type': 'application/json'}

        data = {'type': type}
        url = '/'.join([base_url, ml_workflow_id, 'jobs'])
        url = url.format(self.topic_api_url, self.tenant, project_id)
        res = self._perform_request(
            'post', url, data=json.dumps(data), headers=headers)
        return self._process_response(res, [201])

    def get_machinelearning_jobs(self, project_id, ml_workflow_id):
        """Return all the Machine Learning jobs for a particular Machine
        Learning workflow.

        :param project_id: Id of the Squirro project.
        :param ml_workflow_id: Id of the Machine Learning workflow.
        """
        base_url = '{}/v0/{}/projects/{}/machinelearning_workflows'
        headers = {'Content-Type': 'application/json'}

        url = '/'.join([base_url, ml_workflow_id, 'jobs'])
        url = url.format(self.topic_api_url, self.tenant, project_id)
        res = self._perform_request('get', url, headers=headers)
        return self._process_response(res)

    def get_machinelearning_job(self, project_id, ml_workflow_id, ml_job_id,
                                include_run_log=None, last_n_log_lines=None):
        """Return a particular Machine Learning job.

        :param project_id: Id of the Squirro project.
        :param ml_workflow_id: Id of the Machine Learning workflow.
        :param ml_job_id: Id of the Machine Learning job.
        :param include_run_log: Boolean flag to optionally fetch the last run
            log of the job.
        :param last_n_log_lines: Integer to fetch only the last n lines of the
            last run log.
        """
        base_url = '{}/v0/{}/projects/{}/machinelearning_workflows'
        headers = {'Content-Type': 'application/json'}

        url = '/'.join([base_url, ml_workflow_id, 'jobs', ml_job_id])
        url = url.format(self.topic_api_url, self.tenant, project_id)

        params = {}
        if include_run_log:
            params['include_run_log'] = include_run_log
        if last_n_log_lines:
            params['last_n_log_line'] = last_n_log_lines

        res = self._perform_request('get', url, params=params, headers=headers)
        return self._process_response(res)

    def delete_machinelearning_job(self, project_id, ml_workflow_id,
                                   ml_job_id):
        """Delete a Machine Learning job.

        :param project_id: Id of the Squirro project.
        :param ml_workflow_id: Id of the Machine Learning workflow.
        :param ml_job_id: Id of the Machine Learning job.
        """
        base_url = '{}/v0/{}/projects/{}/machinelearning_workflows'
        headers = {'Content-Type': 'application/json'}

        url = '/'.join([base_url, ml_workflow_id, 'jobs', ml_job_id])
        url = url.format(self.topic_api_url, self.tenant, project_id)
        res = self._perform_request('delete', url, headers=headers)
        return self._process_response(res, [204])

    def kill_machinelearning_job(self, project_id, ml_workflow_id,
                                 ml_job_id):
        """Kills a Machine Learning job if it is running.

        :param project_id: Id of the Squirro project.
        :param ml_workflow_id: Id of the Machine Learning workflow.
        :param ml_job_id: Id of the Machine Learning job.
        """
        base_url = '{}/v0/{}/projects/{}/machinelearning_workflows'
        headers = {'Content-Type': 'application/json'}

        url = '/'.join([base_url, ml_workflow_id, 'jobs', ml_job_id, 'kill'])
        url = url.format(self.topic_api_url, self.tenant, project_id)
        res = self._perform_request('post', url, headers=headers)
        return self._process_response(res, [200])
