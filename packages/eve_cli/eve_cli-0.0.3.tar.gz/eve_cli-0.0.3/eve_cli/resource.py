# -*- coding: utf-8 -*-

import requests
import json
from dateutil.parser import parse as parse_date
from .document import BaseDocument
from .exceptions import exception_handler


def _parse_string(value):

    return str(value)


def _parse_date(value):

    return parse_date(value)


def _parse_dict(value):

    return value


def _parse_int(value):

    return int(value, 10)


def _parse_params(params):

    """ Parse a dict to an eve url parameter

        :param params: Parameters to parse

            >>> client.project._parse_params({
                    "where": {
                        "name": "foo"
                    }
                })
            >>> '?where={"name": "foo"}'

    """

    out = "?_s=eve_cli"
    for key in params:
        out += "&{}={}".format(key, json.dumps(params[key]))
    return out


class Resource(object):

    def __init__(self, resource_name, model_cls=BaseDocument, url="http://localhost", headers={}):

        self._resource_name = resource_name
        self._model_cls = model_cls
        self._url = url
        self._headers = headers

    def _instanciate_model(self, json):

        """ Instanciate a model_cls from a json response

            :param json: The json data describing the item
        """

        item = self._model_cls()
        attributes = list(dir(item))
        value = None
        for attr in attributes:
            if attr in json and type(attr) == str:
                value = {
                    'string': _parse_string,
                    'date': _parse_date,
                    'dict': _parse_dict,
                    'int': _parse_int,
                }.get(getattr(item, attr), lambda x: x)(json.get(attr, ''))
                setattr(item, attr, value)
            else:
                if getattr(item, attr) in ['string', 'date', 'dict', 'int']:
                    setattr(item, attr, None)
        return item

    def get(self, _id):

        """ Perform a GET request on a specific item

            :param _id: The item id

                >>> project = client.project.get(_id="5a80cb56fbba910009780209")

            Retrieve a model_cls instance
        """

        try:
            r = requests.get(self._url + '/{}/{}'.format(self._resource_name, _id), headers=self._headers)
        except requests.exceptions.RequestException as e:
            print("[-] RequestException: Failed to connect to {}".format(self._url))
            return
        data = r.json()
        exception_handler(r, data)
        return self._instanciate_model(data)

    def search(self, params={}):

        """ Perform a GET request on a resource endpoint

                >>> projects = client.project.search({'where': {'name': 'foo'}}) # URL/project?where={"name": "foo"}
                >>> projects
                >>> [] # lol

            :param params: The params to give in the url
        """

        try:
            r = requests.get(self._url + "/{}{}".format(self._resource_name,
                                                        _parse_params(params)
                                                        ),
                             headers=self._headers
                             )
        except requests.exceptions.RequestException as e:
            print("[-] RequestException: Failed to connect to {}".format(self._url))
            return
        data = r.json()
        exception_handler(r, data)
        return [self._instanciate_model(item) for item in data.get('_items', [])]

    def create(self, **kwargs):

        """ Perform a POST on the resource to create a new document/item

            :param kwargs: Resource attrbutes to set for the creation

                >>> project = client.project.create(name="Test", description="Test description")
                >>> project._id
                >>> [...]

        """

        for attr in kwargs:
            if getattr(self._model_cls(), attr) is None:
                print("[-] Unknown field {}".format(attr))
                return
        try:
            r = requests.post(self._url + "/{}".format(self._resource_name), json=kwargs, headers=self._headers)
        except requests.exceptions.RequestException as e:
            print("[-] RequestException: Failed to connect to {}".format(self._url))
            return
        data = r.json()
        exception_handler(r, data)
        return self._instanciate_model(data)

    def delete(self, _id, _etag):

        """ Perform a DELETE request on a resource item

            :param _id: Item ID
            :param _etag: Item Etag

                >>> for project in client.projects.iterate(): # CAUTION: Delete all the projects
                        client.projects.delete(project._id, project._etag)
                >>> # ok
        """

        headers = self._headers.copy()
        headers['If-Match'] = _etag
        try:
            r = requests.delete(self._url + "/{}/{}".format(self._resource_name,
                                                            _id
                                                            ),
                                headers=headers
                                )
        except requests.exceptions.RequestException as e:
            print("[-] RequestException: Failed to connect to {}".format(self._url))
            return
        data = r.json()
        exception_handler(r, data)
        return 'ok'

    def patch(self, _id, _etag, params={}):

        """ Perform a PATCH request on a resource item

            :param _id: Item ID
            :param _etag: Item Etag
            :param _params: The fields to change

                >>> for project, i in enumerates(client.projects.iterate()): # CAUTION: Change all the projects name
                        client.projects.delete(project._id, project._etag, {"name": "Project #{}}".format(i)})
                >>> # ok
        """

        headers = self._headers.copy()
        headers['If-Match'] = _etag
        try:
            r = requests.patch(self._url + "/{}/{}".format(self._resource_name,
                                                           _id
                                                           ),
                               headers=headers,
                               json=params
                               )
        except requests.exceptions.RequestException as e:
            print("[-] RequestException: Failed to connect to {}".format(self._url))
            return
        data = r.json()
        exception_handler(r, data)
        return self._instanciate_model(data)

    def iterate(self, max_results=25, params={}):

        """ Perform an iteration over all the item matching params by group of max_results

            >>> len(list(client.project.iterate()))
            >>> 13
        """

        return EveIterator(self,
                           self._resource_name,
                           url=self._url,
                           max_results=max_results,
                           params=params,
                           headers=self._headers)


class EveIterator:

    def __init__(self, client, resource_name, url="http://localhost/", max_results=25, params={}, headers={}):

        params = params.copy()
        params['max_results'] = max_results
        self._client = client
        self._max_results = max_results
        self._params = params
        self._headers = headers
        self._queue = []
        self._url = url.rstrip('/')
        self._url += "/{}".format(resource_name)
        self._page = 1

    def _fill_queue(self):

        """ Fill the queue with max_results item """

        params = self._params.copy()
        params['page'] = self._page
        try:
            r = requests.get(self._url + _parse_params(params), headers=self._headers)
        except requests.exceptions.RequestException as e:
            print("[-] RequestException: Failed to connect to {}".format(self._url))
            return
        data = r.json()
        exception_handler(r, data)
        for document in data.get('_items', []):
            self._queue.append(self._client._instanciate_model(document))
        self._page += 1

    def __iter__(self):
        return self

    def __next__(self):
        if len(self._queue) == 0:
            self._fill_queue()
        if len(self._queue) == 0:
            raise StopIteration
        return self._queue.pop()
