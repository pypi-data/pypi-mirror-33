from nornir.plugins.tasks.apis import gw
from nornir.core import Task


def sros_bgp_route(task, **params):
    host_name = task.host.name
    type = task.nornir.inventory.hosts[host_name].get("type")
    rib_prefix = ""
    if type == "nokia_sros":
        sub_task = Task(gw.GwRequest, resource="rib", **params)
        r = sub_task.start(task.host, task.nornir)
        if getattr(r, "response", None) and r.response[0].ok:
            rib_prefix = r.result.get("prefix")
        else:
            return {}
    #            raise Exception(f"failed to get RIB route for {params.get('prefix')}: status:{r.status_code}")
    else:
        rib_prefix = params.get("prefix")
    if rib_prefix:
        sub_task = Task(
            gw.GwRequest,
            resource="bgp_rib",
            family=params.get("family"),
            prefix=rib_prefix,
        )
        r = sub_task.start(task.host, task.nornir)
        return r[0]
    return {}
