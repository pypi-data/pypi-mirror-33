import math

from docker_ascii_map.docker_config import Configuration, Container
from docker_ascii_map.widget import *


def build_container_widget(container: Container, encoding: str) -> Widget:
    lines = []

    if encoding == 'UTF-8':
        statuschar = u"\u2713" if container.is_running() else u"\u274c"
    else:
        statuschar = 'V' if container.is_running() else 'x'

    color = 'green' if container.is_running() else 'red'

    lines.append('[' + statuschar + '] ' + container.name)
    lines.append('    ' + container.image)
    container_widget = Paragraph(lines, color=color)
    return container_widget


def build_ordered_network_list(config: Configuration) -> List[str]:
    networks = set()

    for container in config.containers:
        for net in container.networks:
            networks.add(net)

    networks = list(networks)
    networks.sort()

    # Networks are sorted, now group the ones linked by containers

    for container in config.containers:
        if len(container.networks) > 1:
            base_index = networks.index(container.networks[0])
            for net in container.networks[1:]:
                networks.remove(net)
                base_index += 1
                networks.insert(base_index, net)

    return networks


def build_container_wrapper(container: Container, container_widget: Widget) -> Widget:
    ports_count = len(container.ports)
    total_padding = ports_count - 2

    if total_padding <= 0:
        return container_widget
    else:
        return Padding(container_widget,
                       Size(0, int(math.floor(total_padding / 2))),
                       Size(0, int(math.ceil(total_padding / 2))))


class Renderer:
    def __init__(self):
        pass

    def render_to_raster(self, config: Configuration, encoding: str = 'UTF-8'):
        network_widgets = []

        networks = build_ordered_network_list(config)

        net_widgets_map = {}
        cnt_widgets_map = {}

        # Network boxes with single-network containers

        for net in networks:
            net_widgets = []

            for container in config.containers:
                if [net] == container.networks:
                    container_widget = build_container_widget(container, encoding)
                    cnt_widgets_map[container] = container_widget
                    net_widgets.append(build_container_wrapper(container, container_widget))

            net_box = Border(VBox(net_widgets), net)
            net_widgets_map[net] = net_box
            network_widgets.append(net_box)

        # Containers connected to multiple networks

        bridge_widgets = []
        links = []

        for container in config.containers:
            if len(container.networks) > 1:
                c = Padding(build_container_widget(container, encoding), Size(1, 0))
                cnt_widgets_map[container] = c
                padded = Padding(c, Size(12, 2))
                bridge_widgets.append(padded)

                for n in container.networks:
                    net_box = net_widgets_map[n]
                    links.append((c, net_box))

        networks_box = VBox(network_widgets)
        bridges_box = VBox(bridge_widgets)
        links_box = Links(bridges_box, networks_box, links, True)

        # Port mapping

        portmaps = []

        for container in config.containers:
            for port in container.ports:
                w = cnt_widgets_map[container]
                portmaps.append((w,
                                 str(port.public_port),
                                 'green' if container.is_running() else 'red',
                                 []
                                 ))

        ports_box = Annotations(links_box, portmaps)

        root_box = ports_box
        return root_box.render()

    def render_to_string(self, config: Configuration, encoding: str = 'UTF-8', color: bool = False):
        raster = self.render_to_raster(config, encoding)
        return raster.text(color)

    def render(self, config: Configuration, encoding: str = 'UTF-8', color: bool = False):
        return self.render_to_string(config, encoding, color)
