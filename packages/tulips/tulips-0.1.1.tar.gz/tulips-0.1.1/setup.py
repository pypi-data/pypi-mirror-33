# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['tulips', 'tulips.kind']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=3.12,<4.0', 'black>=18.4-alpha.0,<19.0', 'kubernetes>=6.0,<7.0']

setup_kwargs = {
    'name': 'tulips',
    'version': '0.1.1',
    'description': 'Wrapper around kubernetes-clients/python',
    'long_description': "[![Build Status](https://travis-ci.com/dz0ny/tulips.svg?branch=master)](https://travis-ci.com/dz0ny/tulips)\n\n# Tulips\n\nA small wrapper around https://github.com/kubernetes-client/python which understands Kubernetes charts.\n\n## Why\n\nI needed something simple that would read Kubernetes charts and push them to the Kubernetes cluster and\nbe extensible. So something like helm+kubectl with ability to write you own tools around them.\n\n## Supported CRDS aka Kubernetes objects\n\n- Deployment\n- Service\n- Ingress\n- Secret\n- Issuer (cert-manager)\n- PersistentVolumeClaim\n\n## Example\n\n```python\n\nimport yaml\nfrom tulips import class_for_kind\nfrom kubernetes import client as k8s\n\n\nspec = yaml.load('ingress.yaml')\n\ningress_cls = class_for_kind(spec['kind'])\ningress = ingress_cls(config.client)\ningress.create(namespace='default')\nprint ingress.status(namespace='default')\ningress.delete(namespace='default')\n```\n\n## TODO\n\n- [ ] Custom container for yaml(eliminates class_for_kind function)\n- [ ] Simple HELM like CLI tool.\n",
    'author': 'Janez Troha',
    'author_email': 'dz0ny@ubuntu.si',
    'url': 'https://github.com/dz0ny/tulips',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
