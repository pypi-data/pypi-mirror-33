import os
from docker_emperor.utils import combine, memoized_property, yaml


__all__ = ['HasEnvironment', 'Environment']


class HasEnvironment():

    preserve_environment = False
    
    @memoized_property
    def environment(self):
        if self.preserve_environment:
            self.data['environment'] = Environment(self.data.get('environment', {}))
            return self.data['environment']
        else:
            return Environment(self.data.pop('environment', {}))


class Environment(list):

    def __init__(self, value, *args, **kwargs):
        if not isinstance(value, list):
            if isinstance(value, dict):
                value = ['{}={}'.format(key,val) for key,val in value.items()]
            else:
                value = []
        self.dict = dict()
        for var in value:
            key, val = var.split('=', 1) 
            self.dict[key.strip()] = val.strip()
        list.__init__(self, value, *args, **kwargs)
    
    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.dict)

    def __gt__(self, env):
        if not isinstance(env, Environment): return self
        return env < self

    def __lt__(self, env):
        if not isinstance(env, Environment): return self
        del self[:]
        self.__init__(combine(env.dict, self.dict))
        return self

    def items(self):
        return self.dict.items()

    def __dict__(self, key):
        return self.dict

    def get(self, key, default):
        return self[key] or default

    def __getitem__(self, key):
        return self.dict.get(key)

    def __iter__(self):
        for key, val in self.items():
            yield key, val

    def __set__(self, value):
        del self[:]
        self[:] = value        

    @property
    def data(self): return self.dict


def environment_representer(dumper, environment):
    return dumper.represent_list(["{}={}".format(key, val) for key, val in environment.items()])
yaml.add_representer(Environment, environment_representer)