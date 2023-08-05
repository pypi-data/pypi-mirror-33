#!/usr/bin/env python

import scapy.all as scapy
from celery_connectors.utils import ev
from spylunking.log.setup_logging import build_colorized_logger
from network_pipeline.handle_packets import handle_packets


name = "cap-telnet"
log = build_colorized_logger(
    name=name,
    config="capture-telnet-logging.json")


def capture_tcp_packets_over_telnet():
    """capture_tcp_packets_over_telnet

    Capture ``TCP`` packets over telnet
    and call the ``handle_packets`` method

    Change the network interface by ``export CAP_DEVICE=eth0``

    """
    dev = ev(
        "CAP_DEVICE",
        "lo")

    """
    Ignore ports for forwarding to consolidators:

    Redis VM: 6379, 16379
    RabbitMQ VM: 5672, 15672, 25672

    """

    # http://biot.com/capstats/bpf.html
    default_filter = ("tcp and ( port 23 )")
    custom_filter = ev(
        "NETWORK_FILTER",
        default_filter)

    log.info(("starting device={} filter={}")
             .format(
                dev,
                custom_filter))

    scapy.sniff(
        filter=custom_filter,
        prn=handle_packets)

    log.info("done")

# end of capture_tcp_packets_over_telnet


if __name__ == "__main__":
    capture_tcp_packets_over_telnet()
