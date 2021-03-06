from kubernetes import client, config, watch
import asyncio, logging
import os, sys
from clusters import cluster_config_file_paths

ANN_KEY = os.environ.get('ANN_KEY','hayde.trendyol.io/enabled')
ANN_VALUE = os.environ.get('ANN_VALUE', 'true')
NGINX_CONFIG_PATH = os.environ.get('NGINX_CONFIG_PATH', '/etc/nginx/conf.d/')
DOMAIN_NAME = os.environ.get("DOMAIN_NAME", 'sipirsipirmin.com')


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

class ServiceAnnotationWatcher:
    def __init__(self, config_file, cluster_index):
        self.config_file = config_file
        self.kube_client = self.initialize_kube_client()
        self.cluster_index = cluster_index
        all_services = self.get_services()
        self.compatible_services = self.get_annotation_compatible_services(all_services)
        create_nginx_configuration_file_for_compatible_services(self.compatible_services, self.cluster_index )

    def initialize_kube_client(self):
        config.load_kube_config(config_file=self.config_file)
        return client.CoreV1Api()

    def get_services(self):
        return self.kube_client.list_service_for_all_namespaces(watch=False)

    def get_annotation_compatible_services(self, services):
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
    
    async def fallow_the_white_rabbit(self):
        try:
            w = watch.Watch()
            for event in w.stream(self.kube_client.list_service_for_all_namespaces, _request_timeout=120):
                tmp_compatible_services = self.get_annotation_compatible_services(
                                                                self.get_services())
                
                if len(self.compatible_services.keys()) != len(tmp_compatible_services.keys()): # h??mm!
                    self.compatible_services = tmp_compatible_services
                    service_name = event['object'].metadata.name
                    logger.info("Event: %s %s %s" % (event['type'], event['object'].kind, service_name))
                    create_nginx_configuration_file_for_compatible_services(tmp_compatible_services, self.cluster_index )
                    await asyncio.sleep(0)
        except Exception as e:
            logger.info("something happened")
            logger.error(e)
            w.stop()
            sys.exit(1)
        


def get_nginx_template():
    template_file = open("nginx.conf.template", "r")
    template = template_file.read()
    template_file.close()
    
    return template


def create_nginx_configuration_file_for_compatible_services(compatible_services, cluster_index):
    nginx_template = get_nginx_template()
    services_configs = []    
    for service_name in compatible_services.keys():
        nginx_server_name = '.'.join([service_name, DOMAIN_NAME])
        services_configs.append(nginx_template %(
                                            nginx_server_name,compatible_services[service_name]['cluster_ip'],
                                            compatible_services[service_name]['port'])
                                            )
    cluster_config_file = '.'.join([str(cluster_index), 'conf'])
    nginx_config_file = open(os.path.join(NGINX_CONFIG_PATH,cluster_config_file), 'w')
    nginx_config_file.write('\n'.join(services_configs))
    nginx_config_file.close()
    
    os.system("systemctl reload nginx")  # well..


clusters = []

if __name__ == "__main__":
    # initialize cluster watchers
    ioloop = asyncio.get_event_loop()
    for index, cluster_config_file_path in enumerate(cluster_config_file_paths):
        clusters.append(ServiceAnnotationWatcher(config_file=cluster_config_file_path, cluster_index=index))
        ioloop.create_task(clusters[index].fallow_the_white_rabbit())
    ioloop.run_forever()