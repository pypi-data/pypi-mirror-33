import logging

from packy_agent.modules.traceroute.methods.udp import (receive_icmp_reply_basic,
                                                        does_payload_match,
                                                        get_sent_time_from_payload)
from packy_agent.modules.traceroute.methods.base import guess_reply_hop_number

logger = logging.getLogger(__name__)


def process_udp_probe(sent_probes, icmp_socket, finish_time):
    (ip_address, ip_packet, icmp_packet, udp_packet, udp_payload,
     is_destination_reached, is_probe_response) = receive_icmp_reply_basic(icmp_socket)
    if not is_probe_response:
        logger.debug('Discarded ICMP packet type:{} code:{} from {}'.format(
            icmp_packet.type, icmp_packet.code, ip_address))
        return

    probe_port = udp_packet.dst_port
    sent_probe = sent_probes.pop(probe_port, None)
    if not sent_probe:
        logger.debug('Discarded ICMP packet type:{} code:{} from {} '
                     '(UDP destination port {})'.format(
                      icmp_packet.type, icmp_packet.code, ip_address, probe_port))
        return

    if not does_payload_match(sent_probe.payload, udp_payload, icmp_packet, ip_address):
        return

    sent_time_from_payload = get_sent_time_from_payload(udp_payload)
    if sent_time_from_payload is None:
        actual_sent_time = sent_probe.sent_time
    else:
        actual_sent_time = sent_time_from_payload

    from packy_agent.modules.traceroute.base import ProbeResult
    return ProbeResult(
        hop_number=sent_probe.ttl,
        reply_hop_number=guess_reply_hop_number(ip_packet.ttl),
        probe_number=sent_probe.probe_number,
        hop_ip_address=ip_address,
        rtt_seconds=finish_time - actual_sent_time,
        is_destination_reached=is_destination_reached)
