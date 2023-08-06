# -*- coding: utf-8 -*-
import functools
import os

from os_brick import exception
from os_brick.initiator import connector
from os_brick.initiator import connectors
from os_brick.privileged import rootwrap
from oslo_concurrency import processutils as putils
from oslo_privsep import priv_context
from oslo_utils import fileutils


__author__ = """Gorka Eguileor"""
__email__ = 'geguileo@redhat.com'
__version__ = '0.0.1'


class RBDConnector(connectors.rbd.RBDConnector):
    """"Connector class to attach/detach RBD volumes locally.

    OS-Brick's implementation covers only 2 cases:

    - Local attachment on controller node.
    - Returning a file object on non controller nodes.

    We need a third one, local attachment on non controller node.
    """
    def connect_volume(self, connection_properties):
        # NOTE(e0ne): sanity check if ceph-common is installed.
        try:
            self._execute('which', 'rbd')
        except putils.ProcessExecutionError:
            msg = 'ceph-common package not installed'
            raise exception.BrickException(msg)

        # Extract connection parameters and generate config file
        try:
            user = connection_properties['auth_username']
            pool, volume = connection_properties['name'].split('/')
            cluster_name = connection_properties.get('cluster_name')
            monitor_ips = connection_properties.get('hosts')
            monitor_ports = connection_properties.get('ports')
            keyring = connection_properties.get('keyring')
        except IndexError:
            msg = 'Malformed connection properties'
            raise exception.BrickException(msg)

        conf = self._create_ceph_conf(monitor_ips, monitor_ports,
                                      str(cluster_name), user,
                                      keyring)

        # Map RBD volume if it's not already mapped
        rbd_dev_path = self.get_rbd_device_name(pool, volume)
        if (not os.path.islink(rbd_dev_path) or
                not os.path.exists(os.path.realpath(rbd_dev_path))):
            cmd = ['rbd', 'map', volume, '--pool', pool, '--conf', conf]
            cmd += self._get_rbd_args(connection_properties)
            self._execute(*cmd, root_helper=self._root_helper,
                          run_as_root=True)

        return {'path': os.path.realpath(rbd_dev_path),
                'conf': conf,
                'type': 'block'}

    def check_valid_device(self, path, run_as_root=True):
        """Verify an existing RBD handle is connected and valid."""
        try:
            self._execute('dd', 'if=' + path, 'of=/dev/null', 'bs=4096',
                          'count=1', root_helper=self._root_helper,
                          run_as_root=True)
        except putils.ProcessExecutionError:
            return False
        return True

    def disconnect_volume(self, connection_properties, device_info,
                          force=False, ignore_errors=False):

        pool, volume = connection_properties['name'].split('/')
        conf_file = device_info['conf']
        dev_name = self.get_rbd_device_name(pool, volume)
        cmd = ['rbd', 'unmap', dev_name, '--conf', conf_file]
        cmd += self._get_rbd_args(connection_properties)
        self._execute(*cmd, root_helper=self._root_helper,
                      run_as_root=True)
        fileutils.delete_if_exists(conf_file)


ROOT_HELPER = 'sudo'


def unlink_root(*links, **kwargs):
    no_errors = kwargs.get('no_errors', False)
    raise_at_end = kwargs.get('raise_at_end', False)
    exc = exception.ExceptionChainer()
    catch_exception = no_errors or raise_at_end
    for link in links:
        with exc.context(catch_exception, 'Unlink failed for %s', link):
            putils.execute('unlink', link, run_as_root=True,
                           root_helper=ROOT_HELPER)
    if not no_errors and raise_at_end and exc:
        raise exc


def init(root_helper='sudo'):
    global ROOT_HELPER
    ROOT_HELPER = root_helper
    priv_context.init(root_helper=[root_helper])

    existing_bgcp = connector.get_connector_properties
    existing_bcp = connector.InitiatorConnector.factory

    def my_bgcp(*args, **kwargs):
        if len(args):
            args = list(args)
            args[0] = ROOT_HELPER
        else:
            kwargs['root_helper'] = ROOT_HELPER
        kwargs['execute'] = rootwrap.custom_execute
        return existing_bgcp(*args, **kwargs)

    def my_bgc(protocol, *args, **kwargs):
        if len(args):
            # args is a tuple and we cannot do assignments
            args = list(args)
            args[0] = ROOT_HELPER
        else:
            kwargs['root_helper'] = ROOT_HELPER
        kwargs['execute'] = rootwrap.custom_execute

        # OS-Brick's implementation for RBD is not good enough for us
        if protocol == 'rbd':
            factory = RBDConnector
        else:
            factory = functools.partial(existing_bcp, protocol)

        return factory(*args, **kwargs)

    connector.get_connector_properties = my_bgcp
    connector.InitiatorConnector.factory = staticmethod(my_bgc)
    if hasattr(rootwrap, 'unlink_root'):
        rootwrap.unlink_root = unlink_root
