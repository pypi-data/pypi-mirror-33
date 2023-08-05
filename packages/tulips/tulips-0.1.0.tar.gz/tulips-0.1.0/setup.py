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
    'version': '0.1.0',
    'description': 'Wrapper around kubernetes-clients/python',
    'long_description': '# Tulips\n\nA small wrapper around https://github.com/kubernetes-client/python which understands Kubernetes charts.\n\n## Why\n\nI needed something simple that would read Kubernetes charts and push them to the Kubernetes cluster and\nbe extensible. So something like helm+kubectl with ability to write you own tools around them.\n\n## Supported CRDS aka Kubernetes objects\n\n- Deployment\n- Service\n- Ingress\n- Secret\n- Issuer (cert-manager)\n- PersistentVolumeClaim\n\n',
    'author': 'Janez Troha',
    'author_email': 'dz0ny@ubuntu.si',
    'url': 'https://github.com/dz0ny/tulips',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
