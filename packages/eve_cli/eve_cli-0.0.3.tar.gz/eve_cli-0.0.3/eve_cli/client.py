# -*- coding: utf-8 -*-

from .resource import Resource


class EveClient(object):

    """ Main class """

    def __init__(self, url="http://localhost", headers={}):

        """ Eve Client Constructor

            :param url: The base url of the service
            :param headers: Optionals headers used for the requests

                >>> client = EveClient(url="http://localhost:1337", headers={'Authorization': 'secret'})

        """

        self._url = url.rstrip('/')
        self._headers = headers
        self._resources = {}

    def register_resource(self, model_cls):

        """ Register a new resource

            :param resource_cls: Must be a Resource class

                >>> client = EveClient(url="http://localhost")
                >>> from resources.project import Project
                >>> client.register_resource(Project)

        """

        resource_name = model_cls.__name__.lower()  # Retrieve the lower case name of the class
        self._resources[resource_name] = Resource(resource_name=resource_name,
                                                  model_cls=model_cls,
                                                  url=self._url,
                                                  headers=self._headers)

    def __getattr__(self, resource_name):

        """ Overload the getattr method to retrieve resource from the _resources array """

        if resource_name in self._resources:
            return self._resources[resource_name]
