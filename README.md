# Cluster service watcher, nginx config creater 


## Installation

`pip install -r requierements.txt`

## Configuration

You can add an clusters_local.py and create a list named `cluster_config_file_paths` and put kubeconfig paths which will watch..

Ex: 
```
cluster_config_file_paths = ['/home/john/Desktop/config','/home/doe/.kube/config']
```

If you specify `None` in cluster_config_file_paths, watcher gets default kube configs in host machine