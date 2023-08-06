

def traceroute_sequential(trace_function_partial, destination_ip_address,
                          probe_count, max_hops):
    destination_hop = max_hops
    is_destination_reached = False
    results = []
    for ttl in xrange(1, destination_hop + 1):
        results_for_ttl = []
        for probe_number in xrange(probe_count):
            received_probe = trace_function_partial(ttl=ttl)
            from packy_agent.modules.traceroute.base import ProbeResult
            if received_probe:
                received_probe = ProbeResult(
                    hop_number=ttl,
                    reply_hop_number=received_probe.reply_hop_number,
                    probe_number=probe_number,
                    hop_ip_address=received_probe.hop_ip_address,
                    rtt_seconds=received_probe.rtt_seconds,
                    is_destination_reached=received_probe.is_destination_reached)

                is_destination_reached = (
                    is_destination_reached or received_probe.is_destination_reached or
                    received_probe.hop_ip_address == destination_ip_address)

            results_for_ttl.append(received_probe)

        results.append(results_for_ttl)

        if is_destination_reached:
            break

    return results
