cluster_config_file_paths = [
                None, # if exists, default KUBECONFIG will be also used
                # ex: '/path/to/kubeconfıg/file',
            ]

try:
    from clusters_local import cluster_config_file_paths
except ImportError:
    pass

