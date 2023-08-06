import requests

from typing import Optional

from dashbase.auth import AuthClient
from dashbase.response import Response, InfoResponse, ClusterOverviewResponse


class LowLevelClient(object):
    def __init__(self, host: str, token: str = None):
        self.headers = {'Accept': 'application/json'}
        if token:
            self.headers["io.dashbase.auth.token"] = token
        self.host = host
        self.verify = True

    def query(self, req, raw=False):
        path = "/v1/query"

        res = requests.post("{}{}".format(self.host, path), json=req.to_dict(), headers=self.headers,
                            verify=self.verify)
        res.raise_for_status()
        if raw:
            return res
        result = Response(res.json())
        result.raw_res = res.json()
        return result

    def all_cluster_info(self):
        # type: () -> ClusterOverviewResponse
        path = "/v1/cluster/all"
        res = requests.get("{}{}".format(self.host, path), headers=self.headers, verify=self.verify)
        res.raise_for_status()
        result = ClusterOverviewResponse(res.json())
        result.raw_res = res.json()
        return result

    def cluster_info(self, name):
        # type: (str) -> ClusterOverviewResponse
        path = "/v1/cluster/{}".format(name)
        res = requests.get("{}{}".format(self.host, path), headers=self.headers, verify=self.verify)
        res.raise_for_status()
        result = ClusterOverviewResponse(res.json())
        result.raw_res = res.json()
        return result

    def tables(self):
        path = "/v1/cluster/tables"
        res = requests.get("{}{}".format(self.host, path), headers=self.headers, verify=self.verify)
        result = ClusterOverviewResponse(res.json())
        result.raw_res = res.json()
        return result

    def info(self, names=None):
        # type: (Optional[list[str]]) -> InfoResponse
        params = {}
        if names:
            params["names"] = names

        path = "/v1/info"
        res = requests.get("{}{}".format(self.host, path), headers=self.headers, verify=self.verify, params=params)
        res.raise_for_status()
        result = InfoResponse(res.json())
        result.raw_res = res.json()
        return result

    def sql(self, sql):
        path = "/v1/sql"
        res = requests.get("{}{}".format(self.host, path), params={"sql": sql}, headers=self.headers,
                           verify=self.verify)
        res.raise_for_status()
        result = Response(res.json())
        result.raw_res = res.json()
        return result


class Client(LowLevelClient):
    def __init__(self, host: str, token: str = None, get_local_token: bool = False):
        if not token and get_local_token:
            token = AuthClient.get_dashbase_token_in_local(host)
        super().__init__(host, token)

    def topn(self, col, numFacets=5, table="*", sql=None):
        if sql is None:
            sql = 'SELECT TOPN("{col}", {numFacets}) as "values" FROM "{table}" LAST 15 MINUTES LIMIT 100'
        res = self.sql(sql=sql.format(col=col, numFacets=numFacets, table=table))
        return res.aggregations.get("values").get("facets")
