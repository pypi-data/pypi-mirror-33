# -*- coding: utf-8 -*-

"""

SQL Database
~~~~~~~~~~~~
This module provides IO functions to the relational edge store.

"""

import logging

from sqlalchemy.exc import IntegrityError, OperationalError

from .cache_manager import Manager

__all__ = [
    'to_database',
    'from_database'
]

log = logging.getLogger(__name__)


def to_database(graph, connection=None, store_parts=True):
    """Stores a graph in a database.

    :param BELGraph graph: A BEL graph
    :param connection: An RFC-1738 database connection string, a pre-built :class:`Manager`, or `None`` for
                        default connection
    :type connection: None or str or pybel.manager.Manager
    :param bool store_parts: Should the graph be stored in the edge store?
    :return: If successful, returns the network object from the database.
    :rtype: Optional[Network]
    """
    manager = Manager.ensure(connection)

    try:
        return manager.insert_graph(graph, store_parts=store_parts)
    except (IntegrityError, OperationalError):
        manager.session.rollback()
        log.exception('Error storing graph')
    except Exception as e:
        manager.session.rollback()
        raise e


def from_database(name, version=None, connection=None):
    """Loads a BEL graph from a database. If name and version are given, finds it exactly with
    :meth:`pybel.manager.Manager.get_network_by_name_version`. If just the name is given, finds most recent
    with :meth:`pybel.manager.Manager.get_network_by_name_version`

    :param str name: The name of the graph
    :param str version: The version string of the graph. If not specified, loads most recent graph added with this name
    :param connection: An RFC-1738 database connection string, a pre-built :class:`Manager`, or ``None``
                        for default connection
    :type connection: None or str or pybel.manager.Manager
    :return: A BEL graph loaded from the database
    :rtype: Optional[BELGraph]
    """
    manager = Manager.ensure(connection)

    if version is None:
        return manager.get_graph_by_most_recent(name)

    return manager.get_graph_by_name_version(name, version)
