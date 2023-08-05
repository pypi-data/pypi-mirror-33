# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['aioacm']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.3,<4.0']

setup_kwargs = {
    'name': 'aioacm-sdk-python',
    'version': '0.3.13',
    'description': 'Python client for ACM with asyncio support.',
    'long_description': '# User Guide\n\n[![Pypi Version](https://badge.fury.io/py/acm-sdk-python.svg)](https://badge.fury.io/py/acm-sdk-python)\n[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/alibaba/acm-sdk-python/blob/master/LICENSE)\n\n## Introduction\n\nPython SDK for ACM with asyncio support.\n\n### Features\n1. Get/Publish/Remove config from ACM server use REST API.\n2. Watch config changes from server.\n3. Auto failover on server failure.\n4. TLS supported.\n5. Address server supported.\n6. Both Alibaba Cloud ACM and Stand-alone deployment supported.\n\n### Supported Python：\n\n5. Python 3.5\n6. Python 3.6\n\n### Supported ACM version\n1. ACM 1.0\n\n### Change Logs\n\n## Installation\n\nFor Python 3.5 and above:\n```shell\npip install aioacm-sdk-python\n```\n\n## Getting Started\n```python\nimport aioacm\n\nENDPOINT = "acm.aliyun.com:8080"\nNAMESPACE = "**********"\nAK = "**********"\nSK = "**********"\n\n# get config\nclient = aioacm.ACMClient(ENDPOINT, NAMESPACE, AK, SK)\ndata_id = "com.alibaba.cloud.acm:sample-app.properties"\ngroup = "group"\nprint(asyncio.get_event_loop()\n      .run_until_complete(client.get(data_id, group)))\n\n# add watch\nimport time\nclient.add_watcher(\n    data_id,\n    group,\n    lambda x:print("config change detected: " + x)\n)\nasyncio.get_event_loop().run_until_complete(asyncio.sleep(5)) # wait for config changes\n\n```\n\n## Configuration\n```\nclient = ACMClient(endpoint, namespace, ak, sk)\n```\n\n* *endpoint* - **required**  - ACM server address.\n* *namespace* - Namespace. | default: `DEFAULT_TENANT`\n* *ak* - AccessKey For Alibaba Cloud ACM. | default: `None`\n* *sk* - SecretKey For Alibaba Cloud ACM. | default: `None`\n\n#### Extra Options\nExtra option can be set by `set_options`, as following:\n\n```\nclient.set_options({key}={value})\n```\n\nConfigurable options are:\n\n* *default_timeout* - Default timeout for get config from server in seconds.\n* *tls_enabled* - Whether to use https.\n* *auth_enabled* - Whether to use auth features.\n* *cai_enabled* - Whether to use address server.\n* *pulling_timeout* - Long polling timeout in seconds.\n* *pulling_config_size* - Max config items number listened by one polling process.\n* *callback_thread_num* - Concurrency for invoking callback.\n* *failover_base* - Dir to store failover config files.\n* *snapshot_base* - Dir to store snapshot config files.\n* *app_name* - Client app identifier.\n* *no_snapshot* - To disable default snapshot behavior, this can be overridden by param *no_snapshot* in *get* method.\n\n## API Reference\n\n### Get Config\n>`ACMClient.get(data_id, group, timeout, no_snapshot)`\n\n* `param` *data_id* Data id.\n* `param` *group* Group, use `DEFAULT_GROUP` if no group specified.\n* `param` *timeout* Timeout for requesting server in seconds.\n* `param` *no_snapshot* Whether to use local snapshot while server is unavailable.\n* `return`\nW\nGet value of one config item following priority:\n\n* Step 1 - Get from local failover dir(default: `${cwd}/acm/data`).\n  * Failover dir can be manually copied from snapshot dir(default: `${cwd}/acm/snapshot`) in advance.\n  * This helps to suppress the effect of known server failure.\n\n* Step 2 - Get from one server until value is got or all servers tried.\n  * Content will be save to snapshot dir after got from server.\n\n* Step 3 - Get from snapshot dir.\n\n### Add Watchers\n>`ACMClient.add_watchers(data_id, group, cb_list)`\n\n* `param` *data_id* Data id.\n* `param` *group* Group, use `DEFAULT_GROUP` if no group specified.\n* `param` *cb_list* List of callback functions to add.\n* `return`\n\nAdd watchers to a specified config item.\n* Once changes or deletion of the item happened, callback functions will be invoked.\n* If the item is already exists in server, callback functions will be invoked for once.\n* Multiple callbacks on one item is allowed and all callback functions are invoked concurrently by `threading.Thread`.\n* Callback functions are invoked from current process.\n\n### Remove Watcher\n>`ACMClient.remove_watcher(data_id, group, cb, remove_all)`\n\n* `param` *data_id* Data id.\n* `param` *group* Group, use "DEFAULT_GROUP" if no group specified.\n* `param` *cb* Callback function to delete.\n* `param` *remove_all* Whether to remove all occurrence of the callback or just once.\n* `return`\n\nRemove watcher from specified key.\n\n### List All Config\n>`ACMClient.list_all(group, prefix)`\n\n* `param` *group* Only dataIds with group match shall be returned, default is None.\n* `param` *group* only dataIds startswith prefix shall be returned, default is None **Case sensitive**.\n* `return` List of data items.\n\nGet all config items of current namespace, with dataId and group information only.\n* Warning: If there are lots of config in namespace, this function may cost some time.\n\n### Publish Config\n>`ACMClient.publish(data_id, group, content, timeout)`\n\n* `param` *data_id* Data id.\n* `param` *group* Group, use "DEFAULT_GROUP" if no group specified.\n* `param` *content* Config value.\n* `param` *timeout* Timeout for requesting server in seconds.\n* `return` True if success or an exception will be raised.\n\nPublish one data item to ACM.\n* If the data key is not exist, create one first.\n* If the data key is exist, update to the content specified.\n* Content can not be set to None, if there is need to delete config item, use function **remove** instead.\n\n### Remove Config\n>`ACMClient.remove_watcher(data_id, group, cb, remove_all)`\n\n* `param` *data_id* Data id.\n* `param` *group* Group, use "DEFAULT_GROUP" if no group specified.\n* `param` *timeout* Timeout for requesting server in seconds.\n* `return` True if success or an exception will be raised.\n\nRemove one data item from ACM.\n\n## Debugging Mode\nDebugging mode if useful for getting more detailed log on console.\n\nDebugging mode can be set by:\n```\nACMClient.set_debugging()\n# only effective within the current process\n```\n\n## CLI Tool\n\nA CLI Tool is along with python SDK to make convenient access and management of config items in ACM server.\n\nYou can use `acm {subcommand}` directly after installation, sub commands available are as following:\n\n```shell\n    add                 add a namespace\n    use                 switch to a namespace\n    current             show current endpoint and namespace\n    show                show all endpoints and namespaces\n    list                get list of dataIds\n    pull                get one config content\n    push                push one config\n    export              export dataIds to local files\n    import              import files to ACM server\n```\n\nUse `acm -h` to see the detailed manual.\n\n## Data Security Options\n\nACM allows you to encrypt data along with [Key Management Service](https://www.aliyun.com/product/kms), service provided by Alibaba Cloud (also known as **KMS**).\n\nTo use this feature, you can follow these steps:\n1. Install KMS SDK by `pip install aliyun-python-sdk-kms`.\n2. Name your data_id with a `cipher-` prefix.\n3. Get and filling all the needed configuration to `ACMClient`, info needed are: `region_id`, `kms_ak`, `kms_secret`, `key_id`.\n4. Just make API calls and SDK will process data encrypt & decrypt automatically.\n\nExample:\n```\nc = acm.ACMClient(ENDPOINT, NAMESPACE, AK, SK)\nc.set_options(kms_enabled=True, kms_ak=KMS_AK, kms_secret=KMS_SECRET, region_id=REGION_ID, key_id=KEY_ID)\n\n# publish an encrypted config item.\nawait c.publish("cipher-dataId", None, "plainText")\n\n# get the content of an encrypted config item.\nawait c.get("cipher-dataId", None)\n```\n\n## Other Resources\n\n* Alibaba Cloud ACM homepage: https://www.aliyun.com/product/acm\n\n\n',
    'author': 'songww',
    'author_email': 'sww4718168@gmail.com',
    'url': 'https://github.com/ioimop/aioacm',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5',
}


setup(**setup_kwargs)
