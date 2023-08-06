from nornir.plugins.tasks.apis import gw


def populate_ip(task):

    r = task.run(gw.GwRequest, resource="l3_interface")
    task.host.data["ipv4_addresses"] = []
    for if_data in r.result["items"]:
        if if_data.get("ipv4_address") and len(if_data["ipv4_address"]) > 0:
            task.host.data["ipv4_addresses"].extend(if_data["ipv4_address"])


def resolve_ip(nornir, ip_address):
    if not ip_address:
        return ""
    for host_name, host_data in nornir.inventory.hosts.items():
        if host_data.data.get("ipv4_addresses"):
            for address in host_data.data["ipv4_addresses"]:
                if ip_address in address:
                    return host_name
    return ""
