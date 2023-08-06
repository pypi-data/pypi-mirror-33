import logging
import pprint
from copy import deepcopy

from nornir.core.task import AggregatedResult, MultiResult, Result

MAX_DEPTH = 3


def filter_result(result, depth=0, show_parent=True, **kwargs):
    """
    Filters the :obj:`nornir.core.task.Result` using k,v-pair marching from **kwargs

    Arguments:
        result (:obj:`nornir.core.task.Result`): from a previous task
        show_parent (`bool`): return parent attribs also if filter match occurs in child
        **kwargs: arbitrary list of keyword arguments used to match attributes against, 
            e.g. lsp_type="rsvp"

    Returns:
        :obj:`nornir.core.task.Result`: copy of result object with filtered results
    """
    if isinstance(result, AggregatedResult):
        filtered = AggregatedResult(name=result.name + "(filtered)")
        host_spec = kwargs.pop("host", None)
        for host, host_data in result.items():
            if host_spec and host_spec not in host:
                continue
            res = filter_result(host_data, **kwargs)
            filtered[host] = res
    elif isinstance(result, MultiResult):
        filtered = MultiResult(name=result.name + "(filtered)")
        for r in result:
            res = filter_result(r, **kwargs)
            filtered.append(res)
    elif isinstance(result, Result):
        filtered = Result(
            result.host, name=result.name + "(filtered)", response=None, result=None
        )
        filtered.result = filter_result(result.result, **kwargs)
        if len(filtered.result):
            filtered.response = result.response
    elif isinstance(result, list):
        filtered = []
        if len(result):
            if isinstance(result[0], dict):
                filtered = [d for d in result if query_dict(d, **kwargs)]
    elif isinstance(result, dict):
        filtered = {}
        if "__count" in result:  # this is a list wrapped into a dict
            filtered["items"] = []
            for item in result["items"]:
                filtered_item = filtered_dict(item, show_parent=show_parent, **kwargs)
                if len(filtered_item):
                    filtered["items"].append(filtered_item)
            filtered["__count"] = len(filtered["items"])
        else:
            filtered = filtered_dict(result, show_parent=show_parent, **kwargs)
    else:
        return result

    return filtered


def filtered_dict(d, show_parent, **kwargs):
    filtered_d = {}
    # if there is a match in root, we return the entire dict
    # but if there is only a match in a child-list, only return those
    if query_dict(
        {k: v for k, v in d.items() if isinstance(v, (str, int, float))}, **kwargs
    ):
        return deepcopy(d)
    for k, v in d.items():
        if isinstance(v, list) and len(v):
            if isinstance(v[0], dict):
                filtered_v = [d for d in v if query_dict(d, **kwargs)]
                if len(filtered_v):
                    filtered_d[k] = filtered_v
    if len(filtered_d) and show_parent:
        for k, v in d.items():
            if isinstance(v, list) and len(v):
                if not isinstance(v[0], dict):
                    filtered_d[k] = v
            elif isinstance(v, (str, float, int)):
                filtered_d[k] = v
    if not len(filtered_d):
        if query_dict(d, **kwargs):
            filtered_d = deepcopy(d)
    return filtered_d


def query_dict(obj, **query):
    if not query:
        return True
    for attr in obj:
        if isinstance(obj[attr], dict):
            res = query_dict(obj[attr], **query)
            if res:
                return True
        if isinstance(obj[attr], list) and len(obj[attr]):
            if isinstance(obj[attr][0], dict):
                for o in obj[attr]:
                    if not query_dict(o, **query):
                        return False
    for key, query_value in query.items():
        negate = False
        if isinstance(query_value, str):
            if query_value[0] == "!":
                negate = True
                query_value = query_value[1:]
        #        if key not in obj:
        #            return True
        elif isinstance(query_value, (int, float)):
            query_value = str(query_value)
        if isinstance(obj.get(key), list):
            if len(obj[key]) == 0:
                if not negate:
                    return False
            for v in obj[key]:
                if v.find(query_value) == -1:
                    if not negate:
                        return False
                else:
                    if negate:
                        return False
        elif isinstance(obj.get(key), str):
            if obj[key].find(query_value) == -1:
                if not negate:
                    return False
            else:
                if negate:
                    return False
        elif isinstance(obj.get(key), (int, float)):
            try:
                if query_value[0] == "=":
                    if int(obj[key]) != int(query_value[1:]):
                        return False
                elif query_value[0] == ">":
                    if int(obj[key]) <= int(query_value[1:]):
                        return False
                elif query_value[0] == "<":
                    if int(obj[key]) >= int(query_value[1:]):
                        return False
                elif int(query_value) != int(obj[key]):
                    return False
            except ValueError:
                return False
        else:
            return False
    return True
