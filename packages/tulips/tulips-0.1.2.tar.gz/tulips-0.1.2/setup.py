# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['tulips', 'tulips.kind']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=3.12,<4.0',
 'black>=18.4-alpha.0,<19.0',
 'click>=6.7,<7.0',
 'kubernetes>=6.0,<7.0',
 'passlib>=1.7,<2.0',
 'structlog>=18.1,<19.0']

entry_points = \
{'console_scripts': ['tulip = tulips:__main__.cli']}

setup_kwargs = {
    'name': 'tulips',
    'version': '0.1.2',
    'description': 'Wrapper around kubernetes-clients/python',
    'long_description': "[![Build Status](https://travis-ci.com/dz0ny/tulips.svg?branch=master)](https://travis-ci.com/dz0ny/tulips)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n[![Type checker: mypy](https://img.shields.io/badge/type%20checker-mypy-1F5082.svg)](https://github.com/python/mypy)\n[![Packaging: poetry](https://img.shields.io/badge/packaging-poetry-C2CAFD.svg)](https://poetry.eustace.io/)\n\n# Tulips\n\nA small wrapper around https://github.com/kubernetes-client/python which understands Kubernetes charts.\n\n## Why\n\nI needed something simple that would read Kubernetes charts and push them to the Kubernetes cluster and\nbe extensible. So something like helm+kubectl with ability to write you own tools around them.\n\n## Supported CRDS aka Kubernetes objects\n\n- Deployment\n- Service\n- Ingress\n- Secret\n- Issuer (cert-manager)\n- PersistentVolumeClaim\n\n## Example\n\n```python\n\nimport yaml\nfrom tulips import class_for_kind\nfrom kubernetes import client as k8s\n\n\nspec = yaml.load('ingress.yaml')\n\ningress_cls = class_for_kind(spec['kind'])\ningress = ingress_cls(config.client)\ningress.create(namespace='default')\nprint ingress.status(namespace='default')\ningress.delete(namespace='default')\n```\n\n## Tulip\n\nTulip is a sample client that emulates Helm but without `Tiller`.\n\n```shell\n$ python tulips push --help                                    06/25/18 -  9:49\nUsage: tulips push [OPTIONS] CHART\n\n  You can pass chart variables via foo=bar, for example '$ tulip push\n  app.yaml foo=bar'\n\nOptions:\n  --namespace TEXT   Kubernetes namespace\n  --release TEXT     Name of the release\n  --kubeconfig PATH  Path to kubernetes config\n  --help             Show this message and exit.\n\n```\n\n\n### Example\n\n\n\n\n## TODO\n\n- [ ] Custom container for yaml(eliminates class_for_kind function)\n\n",
    'author': 'Janez Troha',
    'author_email': 'dz0ny@ubuntu.si',
    'url': 'https://github.com/dz0ny/tulips',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
