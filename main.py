from kubernetes import client, config
import os

ANN_KEY = 'hayde.trendyol.io/enabled'
ANN_VALUE = 'true'
NGINX_CONFIG_PATH = '/etc/nginx/conf.d/'
DOMAIN_NAME = 'sipirsipirmin.com'


def initialize_kube_client():
    config.load_kube_config()
    v1 = client.CoreV1Api()
    return v1

def get_services(kube_client):
    return kube_client.list_service_for_all_namespaces(watch=False)

def get_annotation_compatible_services(services):
    annotation_positive = dict()

    for i in services.items:
        if i.metadata.annotations is None or i.metadata.annotations.get(ANN_KEY) is None:
            continue
        
        if i.metadata.annotations[ANN_KEY] == ANN_VALUE:
            if i.spec.cluster_ip != "None":
                annotation_positive[i.metadata.name] = dict()
                annotation_positive[i.metadata.name]['cluster_ip'] = i.spec.cluster_ip
                annotation_positive[i.metadata.name]['port'] = i.spec.ports[0].port
        return annotation_positive

def get_nginx_template():
    template_file = open("nginx.conf.template", "r")
    template = template_file.read()
    template_file.close()
    return template

def create_nginx_configuration_file_for_compatible_services(compatible_services, nginx_template):
    for service_name in compatible_services.keys():
        nginx_server_name = '.'.join([service_name, DOMAIN_NAME])
        nginx_conf_file_name = '.'.join([nginx_server_name, 'conf'])
        nginx_conf_file_path = os.path.join(NGINX_CONFIG_PATH, nginx_conf_file_name)

        nginx_config_file = open(nginx_conf_file_path, 'w')
        
        nginx_config_file.write(nginx_template %(
                                            nginx_server_name,compatible_services[service_name]['cluster_ip'],
                                            compatible_services[service_name]['port'])
                                            )
        nginx_config_file.close()

kube_client = initialize_kube_client()
all_services = get_services(kube_client)
compatible_services = get_annotation_compatible_services(all_services)
nginx_template = get_nginx_template()

create_nginx_configuration_file_for_compatible_services(compatible_services, nginx_template)
