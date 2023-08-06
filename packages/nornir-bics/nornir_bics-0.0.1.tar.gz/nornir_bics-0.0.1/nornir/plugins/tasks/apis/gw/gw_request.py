import logging
import time

from nornir.core.task import Result

import requests
from requests.adapters import HTTPAdapter

from requests.packages.urllib3.util.retry import Retry
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

MAX_RETRIES = 3
RETRY_WAIT = 5
RETRY_STATUS_LIST = (500, 502)


class GwRequest(Result):
    """
    GwRequest class deals with REST API requests to the BICS GW. It is a Nornir task
    plugin and its constructor is called as a callable task, whereas typically these are
    standalone functions. As tasks are assumed to return a Nornir Result object, GwRequest
    inherits from :obj:`nornir.core.task.Result`

    Arguments:
        task (object): task object calling this class constructor
        host (str): name of the device to perform request against. Typically, device-name comes 
            via task object when Nornir framework is used. Default: :obj:`nornir.core.task.host
        resource (str): name of resource to perform request against, e.g. 'interface'. Its value
            must be specified in the GwRequest-specific section of the Nornir configuration
        instance (str): name of the resource instance, e.g. '1/1/1'. This will trigger a parametrized
            call to the GW to get a single object containing details of the resource-instance. Usually, this
            is specified if the summary list of instances returned by a request against a resource, does not provide
            sufficient details on the resource instance
        query_all_instances (bool): specifies whether a instance-specific query needs to be performed
            for all instances of the resource. This is an expensive operation as a single call the GwRequest
            will result in individual API calls for each resource instance + a summary resource call. Use carefully!
            Default: False
        method (str): only "get" is supported currently. Default: "get"
        filter (dict): (for "get" requests only) each k,v-pair corresponds to a resource attribute (k) and an expression (v) 
            of the attribute's value. A resource instance is returned if its attributes specified in the filter (keys) and 
            corresponding values match the filter expression (values). E.g. `{'oper_status':'down'}`
        **kwargs: Parameters that will be passed to the class-methods. Some resources have mandatory query-params, e.g. 'bgp_rib'
        These params must be specified as arguments to the class constructor, e.g. `prefix="x.x.x.x/x", vrf=110`


    Attributes:
        task (:obj:`nornir.core.Task`): task object from where this constructor is called
        host (str): name of device to perform request against, defaults to ``task.host``
    """

    def __init__(
        self,
        task=None,
        host=None,
        resource=None,
        instance=None,
        parent=None,
        query_all_instances=False,
        raise_for_status=False,
        method="get",
        auth=None,
        **kwargs,
    ):

        self.task = task
        self.host = host or getattr(task, "host", "n/a")
        self.raise_for_status = raise_for_status
        self.method = method
        if not resource:
            raise ValueError("resource param missing")
        self.resource = resource
        self.query_all_instances = query_all_instances
        self.instance = instance
        self.parent = parent
        self.config = getattr(task.nornir.config, "GwRequest")
        self.resource_config = self.config["endpoints"][resource]
        self.request_timeout = self.config.get("request_timeout")
        self.request_retries = self.config.get("request_retries") or MAX_RETRIES
        self.request_retry_wait = self.config.get("request_retry_wait") or RETRY_WAIT
        self.request_retry_status_list = (
            self.config.get("request_retry_status_list") or RETRY_STATUS_LIST
        )
        self.auth = auth or tuple(self.config.get("auth_params"))
        super().__init__(host=self.host, **kwargs)
        self.result = {}
        self.response = []

        if method == "get":
            self.get(**kwargs)
        elif method == "post":
            raise NotImplementedError
        elif method == "put":
            raise NotImplementedError
        elif method == "delete":
            raise NotImplementedError
        else:
            raise ValueError("Unsupported method: {}".format(method))

    @staticmethod
    def _requests_retry_session(
        retries=3, status_forcelist=RETRY_STATUS_LIST, session=None
    ):
        session = session or requests.Session()
        retry = Retry(total=retries, status_forcelist=status_forcelist)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def _get_request(self, url, filter=None, **kwargs):

        logger = logging.getLogger("nornir")
        t0 = time.time()
        #        r = requests.get(url, auth=self.auth, **kwargs)
        s = requests.Session()
        s.auth = self.auth
        for p, v in kwargs.items():
            setattr(s, p, v)
        try:
            r = self._requests_retry_session(
                session=s,
                retries=self.request_retries,
                status_forcelist=self.request_retry_status_list,
            ).get(url)
        except requests.exceptions.RetryError:
            logger.info("ERROR: get {} retry failed".format(url))
            raise requests.exceptions.RetryError(
                "ERROR: Request for {} timed out".format(url)
            )
        #        n_attempt = 0
        #        while True:
        #            r = s.get(url)
        #            if r.ok or r.status_code not in self.request_retry_status_list:
        #                break
        #            n_attempt += 1
        #            if n_attempt > self.request_retries:
        #                break
        #            logger.info("WARNING: {} retrying {}/{} get {},params:{}, got status:{} in previous request".format(
        #                    self.auth[0], n_attempt, self.request_retries, url, kwargs.get("params"), r.status_code))
        #            time.sleep(self.request_retry_wait)

        t1 = time.time()
        elapsed = t1 - t0
        logger.info(
            "{}, get url:{},params:{} ran for {:.2f}s (resp_code:{})".format(
                self.auth[0], url, kwargs.get("params"), elapsed, r.status_code
            )
        )
        if self.raise_for_status:
            r.raise_for_status()
        if not r.ok:
            logger.info(
                "ERROR: get {}, status:{}, args:{}, {}".format(
                    url, r.status_code, kwargs, r.text
                )
            )
            result = {}
        else:
            try:
                content_type = r.headers["Content-type"]
            except KeyError:
                content_type = "text"

            result = r.json() if "application/json" == content_type else r.text
            if len(result) == 0:
                logger.info(
                    "WARNING: Empty response: {}, status:{}, headers:{}, content:{}".format(
                        r.url, r.status_code, r.headers, r.text
                    )
                )
            if isinstance(result, dict):
                if not filter_it(result, filter):
                    result = {}
            if isinstance(result, list):
                if len(result) and filter:
                    result = [e for e in result if filter_it(e, filter)]

        return result, r

    def get(self, filter=None, **kwargs):

        logger = logging.getLogger("nornir")

        n_calls = 0
        self.task.name = f"get_{self.resource}"
        params = {}
        if "parent" in self.resource_config:
            parent_resource = self.resource_config["parent"]
            parent_rid = self.config["endpoints"][parent_resource]["r_id"]
            if not self.parent:
                raise KeyError(
                    "Resource {} needs parent ({}) instance".format(
                        self.resource, self.resource_config["parent"]
                    )
                )
            else:
                params[parent_rid] = self.parent
        if "mandatory_params" in self.resource_config:
            try:
                for p in self.resource_config["mandatory_params"]:
                    params[p] = kwargs.pop(p)
            except KeyError:
                raise KeyError(
                    "Resource {} has mandatory params - not given".format(self.resource)
                )

        url = "https://{host}/api/{api_version}".format(**self.config)
        url += "/devices/{}{}".format(self.host, self.resource_config["path"])
        t0 = time.time()
        if self.instance:
            self.task.name += f":{self.instance}"
            try:
                r_id = self.resource_config["r_id"]
            except:
                raise Exception(
                    f"Querying an instance required 'r_id' config for resource {self.resource}"
                )
            params[r_id] = self.instance
        if self.query_all_instances:
            self.task.name += ":all_instances"
            try:
                r_id = self.resource_config["r_id"]
            except:
                raise Exception(
                    f"'query_all_instances' requires 'r_id' for resource {self.resource}"
                )
            n_calls += 1
            result, response = self._get_request(
                url,
                filter=None,
                timeout=self.request_timeout,
                verify=False,
                params=params,
            )
            self.response.append(response)
            if response.ok:
                if isinstance(result, list):
                    r_instances = [r[r_id] for r in result]
                    self.result["items"] = []
                    for r_instance in r_instances:
                        params[r_id] = r_instance
                        n_calls += 1
                        instance_result, instance_response = self._get_request(
                            url,
                            filter=filter,
                            timeout=self.request_timeout,
                            verify=False,
                            params=params,
                        )
                        self.response.append(instance_response)
                        if len(instance_result):
                            self.result["items"].append(instance_result)
                    self.result["__count"] = len(self.result["items"])
                else:
                    raise Exception(
                        "Cannot query instances: base url does not return list"
                    )
            else:
                self.result = {}
        else:
            n_calls += 1
            result, response = self._get_request(
                url,
                filter=filter,
                timeout=self.request_timeout,
                verify=False,
                params=params,
                **kwargs,
            )
            self.response.append(response)
            if isinstance(result, list):
                self.result = {"__count": len(result), "items": result}
            else:
                self.result = result
        t1 = time.time()
        elapsed = t1 - t0
        logger.info(
            "{}, host:{}, resource {}, ran for {:.2f}s, {}#req, avg {:.2f}s/req".format(
                self.auth[0],
                self.host,
                self.resource,
                elapsed,
                n_calls,
                elapsed / n_calls,
            )
        )


def filter_it(obj, query):
    if not query:
        return True
    for attr in obj:
        if isinstance(obj[attr], dict):
            res = filter_it(obj[attr], query)
            if res:
                return True
        if isinstance(obj[attr], list) and len(obj[attr]):
            if isinstance(obj[attr][0], dict):
                for o in obj[attr]:
                    if filter_it(o, query):
                        return True

    for key in query:
        negate = False
        query_value = query[key]
        if isinstance(query_value, str):
            if query_value[0] == "!":
                negate = True
                query_value = query_value[1:]
        #        if key not in obj:
        #            return True
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
                else:
                    return True
            except ValueError:
                return False
        else:
            return False
    return True
