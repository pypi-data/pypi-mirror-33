from typing import List

import docker


class PortMapping:
    def __init__(self, private_port: int, public_port: int):
        self.private_port = private_port
        self.public_port = public_port

    def __repr__(self):
        return '%d:%d' % (self.public_port, self.private_port)


class VolumeMapping:
    def __init__(self, rw: bool, source: str, destination: str):
        self.rw = rw
        self.source = source
        self.destination = destination

    def __repr__(self):
        return '%s:%s' % (self.source, self.destination)


class Container:
    def __init__(self, name: str, status: str, networks: List[str], image: str,
                 ports: List[PortMapping] = None,
                 volumes: List[VolumeMapping] = None):
        self.name = name
        self.status = status
        self.networks = networks
        self.image = image
        self.ports = ports if ports is not None else []
        self.volumes = volumes if volumes is not None else []

    def is_running(self):
        return self.status == 'running'

    def __repr__(self) -> str:
        return '%s - %s - %s %s %s' % (self.name, self.status, self.networks, self.ports, self.volumes)


class Configuration:
    def __init__(self, containers: List[Container]):
        self.containers = containers

    def __repr__(self):
        return str([repr(c) for c in self.containers])


class ConfigParser:
    def __init__(self):
        self._client = docker.from_env(assert_hostname=False)

    def get_configuration(self) -> Configuration:
        containers = []

        for cinfo in self._client.containers(all=True):
            name = cinfo['Names'][0]

            if name[0] == '/':
                name = name[1:]

            status = cinfo['State']
            image = cinfo['Image']
            networks = [n for n in cinfo['NetworkSettings']['Networks'].keys()]
            networks.sort()
            ports = [PortMapping(p['PrivatePort'], p['PublicPort'])
                     for p in cinfo['Ports'] if 'PublicPort' in p.keys()]
            volumes = [VolumeMapping(rw=v['RW'], source=v['Source'], destination=v['Destination'])
                       for v in cinfo['Mounts']]
            containers.append(Container(name, status, networks, image, ports, volumes))

        return Configuration(containers)
