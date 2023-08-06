# Elasticsearch cat CLI
Basic Elasticsearch cat API command line wrapper with multi-cluster support

#### Features:
- Complete coverage of all Elasticsearch `cat` modules
- Exposed `cat` API call options as command line arguments
- Get output in form of json, yaml or text
- Manage multiple clusters using profiles
- Support for SSL and Password authentication

### Installation:
**Requirements**:
- python3
- pip

**Installation instructions**
- Install using pip
```
pip install escat
```
- Create a file config file as described in the Configuration section. If you would like to quickly get started, just use the following format and create that file in the destination `~/.escat/config.yml`
```yaml
clusters:
  default:
    hosts: ["http://localhost:9200"]    
```

### Configuration
Example configuration
```yaml
clusters:
  default:
    hosts: ['http://localhost:9200']
#    auth:
#      username: 'elastic'
#      password:
#        ask: yes
#        value: 'elastic'
#    ssl:
#      enabled: no
#      cert: ''
#      ca: []
#      private_key: ''
#      verify_certs: yes
```
The contents of the file are pretty self explanatory. The keys: `auth` and `ssl` are disabled but visible for reference on how to configure authentication for the requests sent to Elasticsearch. Below mentioned is a multi cluster configuration. For the rest of the documentation, we are going to use this configuration file to run commands:
```yaml
clusters:
  default:
    hosts: ['http://localhost:9200']
  dev:
    hosts: ['https://dev-es-1:9200', 'https://dev-es-2:9200']
  prod:
    hosts: ['https://prod-es-1:9200', 'https://prod-es-2:9200']
    ssl:
      enabled: yes
      cert: '~/.openssl/certs/prod-es-cert.cert'
      ca: ['~/.openssl/cas/prod-ca-1.cert', '~/.openssl/cas/prod-ca-2.cert']
      private_key: '~/.openssl/certs/prod-es-cert.key'
      verify_certs: yes
```
If you set a config like this:
```yaml
clusters:
  default:
    hosts: ['http://localhost:9200']
    auth:
      username: 'elastic'
      password:
        ask: yes
```
You will be asked for the password on a command line. 
### Running
To understand some options, please refer the config example directly above
Get help for commands
```
escat -h
```
Get cluster health for default cluster
```
escat health
```
Get count for selective indices in the dev cluster
```
escat --cluster dev count --indices "dev-test"
``` 
Get recovery information on prod cluster in json format
```
escat --cluster prod --format json recovery
```
Use a different config file
```
escat --config ~/.es.yml --cluster dev health
```

### Contributing
Please raise github issues related to questions, feature requests or troubleshooting. Also, to make debug person's life easier, one should always include the following information:
- Command ran
- Operating system
- Python version
- Elasticsearch version

Currently, the escat is only tested on Python 3.6.5 on Ubuntu 16.04, Windows 10, and Mac OSX. 
PRs are welcome. Do mention the description in brief what the PR would fix. If the PR is in a form of checklist, it would be amazing.

### Resources
[Elasticsearch cat API](https://www.elastic.co/guide/en/elasticsearch/reference/current/cat.html)
