import json


class PipelineStatusMixin(object):

    def get_pipeline_status(self, sections=[]):
        """Returns all or the specified status sections of the ingester status.

        :param sections: optional, list of sections to return.
        :return: A status dictionary.
        """
        headers = {'Content-Type': 'application/json'}

        url = '%(ep)s/v0/ingester/status' % {
                'ep': self.topic_api_url}

        data_dict = dict(sections=','.join(sections))

        res = self._perform_request('get', url,
                                    data=json.dumps(data_dict), headers=headers)

        return self._process_response(res)

    def perform_pipeline_action(self, action, action_config=None):
        """Performs an ingester action.

        :param action: string, action to perform
        :param action_config: optional dict, data to be passed to the action
        :return: A status dictionary.

        Currently, only the action "reset" is supported. It does not take
        any action_config and will delete the full ingester backlog.
        """
        headers = {'Content-Type': 'application/json'}

        url = '%(ep)s/v0/ingester/action' % {
                'ep': self.topic_api_url}

        if action_config is None:
            action_config = {}
        assert isinstance(action_config, dict)
        action_config['action'] = action

        res = self._perform_request('post', url,
                                    data=json.dumps(action_config),
                                    headers=headers)

        return self._process_response(res)
