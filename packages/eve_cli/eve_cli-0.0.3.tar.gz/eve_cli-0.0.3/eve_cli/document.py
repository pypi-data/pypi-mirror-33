# -*- coding: utf-8 -*-


class BaseDocument:

    """ Base eve document """

    _created = 'data'
    _updated = 'data'
    _etag = 'string'
    _id = 'string'

    def __str__(self):

        return ("{}<_id={},\n\t_created={},\n\t_updated={},\n\t_etag={}>".format(self.__class__.__name__,
                                                                                 self._id,
                                                                                 self._created,
                                                                                 self._updated,
                                                                                 self._etag))
