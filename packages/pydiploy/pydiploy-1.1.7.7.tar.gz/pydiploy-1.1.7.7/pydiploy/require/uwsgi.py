# -*- coding: utf-8 -*-

"""
"""

import os

import fabric
from fabric.api import env
import fabtools

from pydiploy.decorators import do_verbose


@do_verbose
def root_web():
    """ Creates web root for webserver """

    fabtools.require.files.directory(env.remote_static_root, use_sudo=True,
                                     owner='root', group='root', mode='755')


@do_verbose
def uwsgi_pkg(update=False):
    """ Installs uwsgi package on remote server """

    fabtools.require.deb.packages(['uwsgi'], update=update)


@do_verbose
def uwsgi_start():
    """ Starts uwsgi """

    if not uwsgi_started() and ('uwsgi_force_start' not in env or not env.uwsgi_force_start):
        fabric.api.puts("uwsgi is not started")
    else:
        fabtools.service.start('uwsgi')


@do_verbose
def uwsgi_reload():
    """ Starts/reloads uwsgi """

    if not uwsgi_started():
        if 'uwsgi_force_start' in env and env.uwsgi_force_start:
            fabric.api.execute(uwsgi_start)
        else:
            fabric.api.puts("uwsgi is not started")
    else:
        fabtools.service.reload('uwsgi')


@do_verbose
def uwsgi_restart():
    """ Starts/Restarts uwsgi """

    if not uwsgi_started():
        if 'uwsgi_force_start' in env and env.uwsgi_force_start:
            fabric.api.execute(uwsgi_start)
        else:
            fabric.api.puts("uwsgi is not started")
    else:
        fabtools.service.restart('uwsgi')


@do_verbose
def uwsgi_started():
    """ Returns true/false depending on uwsgi service is started """

    return fabtools.service.is_running('uwsgi')


@do_verbose
def web_configuration():
    """ Setups webserver's configuration """

    uwsgi_root = '/etc/uwsgi'
    uwsgi_available = os.path.join(uwsgi_root, 'apps-available')
    uwsgi_enabled = os.path.join(uwsgi_root, 'apps-enabled')
    app_conf = os.path.join(uwsgi_available, '%s.conf' % env.server_name)

    fabric.api.execute(up_site_config)
    fabric.api.execute(down_site_config)

    if fabtools.files.is_link('%s/default' % uwsgi_enabled):
        with fabric.api.cd(uwsgi_enabled):
            fabric.api.sudo('rm -f default')


@do_verbose
def up_site_config(update=False):
    """ Uploads site config for uwsgi """
    uwsgi_root = '/etc/uwsgi'
    uwsgi_available = os.path.join(uwsgi_root, 'apps-available')
    uwsgi_enabled = os.path.join(uwsgi_root, 'apps-enabled')
    app_conf = os.path.join(uwsgi_available, '%s.conf' % env.server_name)

    fabtools.files.upload_template('uwsgi.ini.tpl',
                                   app_conf,
                                   context=env,
                                   template_dir=os.path.join(
                                       env.lib_path, 'templates'),
                                   use_jinja=True,
                                   use_sudo=True,
                                   user='root',
                                   chown=True,
                                   mode='644')

    if not fabtools.files.is_link('%s/%s.conf' % (uwsgi_enabled,
                                                  env.server_name)):
        with fabric.api.cd(uwsgi_enabled):
            fabric.api.sudo('ln -s %s .' % app_conf)


@do_verbose
def down_site_config():
    """ Uploads site_down config for uwsgi """
    pass
    # uwsgi_root = '/etc/uwsgi'
    # uwsgi_available = os.path.join(uwsgi_root, 'sites-available')
    # app_conf = os.path.join(uwsgi_available, '%s_down.conf' % env.server_name)

    # fabtools.files.upload_template('uwsgi_down.conf.tpl',
    #                                app_conf,
    #                                context=env,
    #                                template_dir=os.path.join(
    #                                    env.lib_path, 'templates'),
    #                                use_jinja=True,
    #                                use_sudo=True,
    #                                user='root',
    #                                chown=True,
    #                                mode='644')

    # fabric.api.execute(upload_maintenance_page)


@do_verbose
def set_website_up():
    """ Sets website up """

    uwsgi_root = '/etc/uwsgi'
    uwsgi_available = os.path.join(uwsgi_root, 'apps-available')
    uwsgi_enabled = os.path.join(uwsgi_root, 'apps-enabled')
    app_conf = os.path.join(uwsgi_available, '%s.conf' % env.server_name)

    if not fabtools.files.is_file(app_conf):
        fabric.api.execute(up_site_config)

    if fabtools.files.is_link('%s/%s_down.conf' % (uwsgi_enabled,
                                                   env.server_name)):
        with fabric.api.cd(uwsgi_enabled):
            fabric.api.sudo('rm -f %s_down.conf' % env.server_name)

    if not fabtools.files.is_link('%s/%s.conf' % (uwsgi_enabled,
                                                  env.server_name)):
        with fabric.api.cd(uwsgi_enabled):
            fabric.api.sudo('ln -s %s .' % app_conf)

    fabric.api.execute(uwsgi_reload)


@do_verbose
def set_website_down():
    """ Sets website down """

    uwsgi_root = '/etc/uwsgi'
    uwsgi_available = os.path.join(uwsgi_root, 'apps-available')
    uwsgi_enabled = os.path.join(uwsgi_root, 'apps-enabled')
    app_down_conf = os.path.join(
        uwsgi_available, '%s_down.conf' % env.server_name)

    if not fabtools.files.is_file(app_down_conf):
        fabric.api.execute(down_site_config)

    if fabtools.files.is_link('%s/%s.conf' % (uwsgi_enabled,
                                              env.server_name)):
        with fabric.api.cd(uwsgi_enabled):
            fabric.api.sudo('rm -f %s.conf' % env.server_name)

    if not fabtools.files.is_link('%s/%s_down.conf' % (uwsgi_enabled,
                                                       env.server_name)):
        with fabric.api.cd(uwsgi_enabled):
            fabric.api.sudo('ln -s %s .' % app_down_conf)

    fabric.api.execute(uwsgi_reload)
