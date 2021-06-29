# Cluster service watcher, nginx config creater 


## Kurulum

https://github.com/sipirsipirmin/ty-case-ansible/tree/master/tycase-tool-ansible kullanılarak kurulum gerçekleştirilebilir.

## Konfigürasyon

clusters_local.py dosyası yaratıldıktan sonra, `cluster_config_file_paths` isminde bir liste oluşturulup, bu listenin içerisinde, kubeconfig dosyalarının path'i belirtilebilir. Belirtilen bu cluster konfigürasyonları kullanılarak, ilgili clusterlardaki servisler takip edilecektir.

Örnek: 
```
cluster_config_file_paths = ['/home/john/Desktop/config','/home/doe/.kube/config']
```

clusters_local.py dosyasının oluşturulmaması veya içerisinde oluşturulan listede `None` elemanının bulunması durumunda, tycase-tool üzerinde çalıştığı makinanın default KUBECONFIG'ine göre hareket edecektir.

## Amaç & Çalışma Prensibi

### Amaç

Konfigürasyonda belirtilen veya default olarak erişilen clusterda bulunun `hayde.trendyol.io/enabled=true` annotation'ınına sahip[1] servislere ait nginx dosyası[2] oluşturmak.

### Çalışma Prensibi

Bağlanılan kubernetes cluster'larındaki servisler asenkron olarak izlenilmektir. Bu servislere, belirtilen annotation eklendiğinde, tycase-tool, servisin ip adresini(cluster-ip)[3] ve port bilgisini[4] alarak, `nginx.conf.template` i kullanarak servise ait bir nginx konfigürasyonu oluşturur.

## NGINX Konfigürasyonu

`nginx.conf.template` dosyasından anlaşılacağı üzere, oluşturulan konfigürasyon aslında bir reverse proxy oluşturmakdır. Bağlı olunan clusterda çalışan servislerin cluster ip'sine reverse proxy yapılmaktadır. Reverse proxy yapılan bu servislere, `servis-adi.sipirsipirmin.com`adresinden ulaşılabilir. Eğer ilgili servise ait bir konfigürasyon yoksa default olarak başka "bir adrese" yönlendirilmektedir. :)

Subdomain olarak servislerin isminin verilmesi cloudflare'da tanımlanan `*.sipirsipirmin.com`kaydının bu tool'un üzerinde çalıştığı makinanın dış ipsine yönlendirilerek sağlanmıştır.



[1] Bu annotation ANN_KEY ve ANN_VALUE environment variableları setlenerek değiştirilebilir.
[2] İlgili nginx dosyası `nginx.conf.template` baz alınarak oluşturulmaktadır.
[3] Aslında izleme esnasında bütün servisleri alıp aralarında annotate edilmişleri ayıklamaktadır. Ayrıca bir önceki nginx konfigürasyonu oluşturma esnasında kullandığı servislerin listesini de tutmaktadır. Eğer oluşturulan yeni annotate edilmiş servis listesindeki eleman sayısı bir önceki oluşturmaya dair listenin eleman sayısından farklıysa, ilgili clusterın nginx konfigürasyonunu tekrar oluşturmaktadır.
[4] Port bilgisinin alınması konusunda bir problem mevcuttur. Bu problem sürekli ilk portun alınmasıdır. Servislerin doğası gereği birden fazla portu olabilir ama bu nokta göz ardı edilmiştir.