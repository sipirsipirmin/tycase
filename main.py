from kubernetes import client, config
from kubernetes.client import configuration

ANN_KEY = 'meta.helm.sh/release-name'
ANN_VALUE = 'prometheus-test'

config.load_kube_config()

v1 = client.CoreV1Api()

ret = v1.list_service_for_all_namespaces(watch=False)

annotateds = []
services = dict()

for i in ret.items:
    if hasattr(i, 'metadata') == False:
        continue
    if i.metadata.annotations is None:
        continue
    if i.metadata.annotations.get(ANN_KEY) is None:
        continue
    if i.metadata.annotations[ANN_KEY] == ANN_VALUE:
        if i.spec.cluster_ip != "None":
            print(i.spec.cluster_ip)
            services[i.metadata.name] = dict()
            services[i.metadata.name]['cluster_ip'] = i.spec.cluster_ip
            services[i.metadata.name]['port'] = i.spec.ports[0].port


template_file = open("nginx.conf.template", "r")
template = template_file.read()
template_file.close()

for service_name in services.keys():
    nginx_server_name = service_name + '.sipirsipirmin.com'
    print(template %(nginx_server_name,services[service_name]['cluster_ip'],services[service_name]['port']))
