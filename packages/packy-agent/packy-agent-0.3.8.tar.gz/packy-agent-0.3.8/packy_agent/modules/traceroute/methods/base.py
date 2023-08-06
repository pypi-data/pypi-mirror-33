def guess_reply_hop_number(ttl):
    if ttl <= 64:
        return 65 - ttl
    elif ttl <= 128:
        return 129 - ttl
    else:
        return 256 - ttl
