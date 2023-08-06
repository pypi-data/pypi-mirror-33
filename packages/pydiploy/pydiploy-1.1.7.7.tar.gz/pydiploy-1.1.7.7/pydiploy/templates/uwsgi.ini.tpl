[uwsgi]
socket = {{ host }}:{{ socket_host }}
chdir = {{ remote_virtualenv_dir }}
{% if framework == "django" %}
pythonpath = ..
env = DJANGO_SETTINGS_MODULE={{ goal }}.{{ application_name }}.settings
module = django.core.handlers.wsgi:WSGIHandler()
{% else %}
wsgi-file = {{ wsgi_file }}
{% endif %}
uid = {{ remote_owner }}
gid = {{ remote_group }}
processes = 4
threads = 2