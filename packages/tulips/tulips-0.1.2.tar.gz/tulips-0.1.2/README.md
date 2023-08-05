[![Build Status](https://travis-ci.com/dz0ny/tulips.svg?branch=master)](https://travis-ci.com/dz0ny/tulips)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Type checker: mypy](https://img.shields.io/badge/type%20checker-mypy-1F5082.svg)](https://github.com/python/mypy)
[![Packaging: poetry](https://img.shields.io/badge/packaging-poetry-C2CAFD.svg)](https://poetry.eustace.io/)

# Tulips

A small wrapper around https://github.com/kubernetes-client/python which understands Kubernetes charts.

## Why

I needed something simple that would read Kubernetes charts and push them to the Kubernetes cluster and
be extensible. So something like helm+kubectl with ability to write you own tools around them.

## Supported CRDS aka Kubernetes objects

- Deployment
- Service
- Ingress
- Secret
- Issuer (cert-manager)
- PersistentVolumeClaim

## Example

```python

import yaml
from tulips import class_for_kind
from kubernetes import client as k8s


spec = yaml.load('ingress.yaml')

ingress_cls = class_for_kind(spec['kind'])
ingress = ingress_cls(config.client)
ingress.create(namespace='default')
print ingress.status(namespace='default')
ingress.delete(namespace='default')
```

## Tulip

Tulip is a sample client that emulates Helm but without `Tiller`.

```shell
$ python tulips push --help                                    06/25/18 -  9:49
Usage: tulips push [OPTIONS] CHART

  You can pass chart variables via foo=bar, for example '$ tulip push
  app.yaml foo=bar'

Options:
  --namespace TEXT   Kubernetes namespace
  --release TEXT     Name of the release
  --kubeconfig PATH  Path to kubernetes config
  --help             Show this message and exit.

```


### Example




## TODO

- [ ] Custom container for yaml(eliminates class_for_kind function)

