[![Build Status](https://travis-ci.com/dz0ny/tulips.svg?branch=master)](https://travis-ci.com/dz0ny/tulips)

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

## TODO

- [ ] Custom container for yaml(eliminates class_for_kind function)
- [ ] Simple HELM like CLI tool.
