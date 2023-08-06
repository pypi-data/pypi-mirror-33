import os
from docker_emperor.nodes import HasEnvironment
from docker_emperor.utils import combine, memoized_property, yaml


__all__ = ['HasServices', 'Services', 'Service']


class HasServices():

    preserve_services = True

    @memoized_property
    def services(self):
        if self.preserve_services:
            self.data['services'] = Services(self.data.get('services', {}))
            return self.data['services']
        else:
            return Services(self.data.pop('services', {}))


class Services(dict):

    def __new__(cls, *args, **kwargs):
        return dict.__new__(cls, *args, **kwargs)

    def __init__(self, data):
        if not isinstance(data, dict): data = {}
        super(Services, self).__init__(data)
        for name, data in self.items(): self[name] = Service(name, data)

    def __gt__(self, services):
        if not isinstance(services, Services): return self
        return services < self

    def __lt__(self, services):
        if not isinstance(services, Services): return self
        for service in services:
            service < self.get(service.name)
        return self

    def __iter__(self):
        for name, service in self.items():
            yield service

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, super(dict, self).__repr__())

    @property
    def data(self): return self

def services_representer(dumper, services):
    return dumper.represent_dict(services)
yaml.add_representer(Services, services_representer)


class Service(HasEnvironment, dict):

    preserve_environment = True

    def __new__(cls, *args, **kwargs):
        return dict.__new__(cls, *args, **kwargs)

    def __init__(self, name, data):
        self.name = name
        if not isinstance(data, dict): data = {}
        super(Service, self).__init__(data)

    def __gt__(self, service):
        if not isinstance(service, Service): return self
        return service < self

    def __lt__(self, service):
        if not isinstance(service, Service): return self
        self.__init__(self.name, combine(service, self))
        return self

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.name)

    @property
    def data(self): return self
    

def service_representer(dumper, service):
    return dumper.represent_dict(service)
yaml.add_representer(Service, service_representer)

#print(Service('test1', { 'key1-test1': 1, 'key2-test1': 1}) < Service('test2', { 'key1-test1': 2, 'key3-test2': 1}))
# print(yaml.dump(Service('test1', { 'key1-test1': 1, 'key2-test1': 1})))