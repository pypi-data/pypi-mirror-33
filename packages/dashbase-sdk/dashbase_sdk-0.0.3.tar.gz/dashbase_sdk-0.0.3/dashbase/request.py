import time
from schematics.models import Model
from schematics.types.base import LongType, StringType, BooleanType, BaseType
from schematics.types.compound import ListType, ModelType, DictType


class TimeRange(Model):
    startTimeInSec = LongType()
    endTimeInSec = LongType()
    endGlobalId = LongType()
    startGlobalId = LongType()


class Request(Model):
    numResults = LongType(default=10)
    tableNames = ListType(StringType, default=["*"])
    excludeTableNames = ListType(StringType, default=[])
    query = DictType(BaseType)
    aggregations = DictType(BaseType)
    timeRangeFilter = ModelType(TimeRange)  # type: TimeRange
    fields = ListType(StringType, default=[])
    useApproximation = BooleanType(default=False)
    ctx = StringType()
    fetchSchema = BooleanType(default=False)
    timeoutMillis = LongType(default=0x7fffffff)
    disableHighlight = BooleanType(default=False)
    startId = StringType()
    endId = StringType()
    debugMode = LongType()


class QueryRequest(object):
    def __init__(self,
                 end_id=None,
                 start_id=None,
                 table=None,
                 query=None,
                 num=10,
                 fields=None,
                 disable_highlight=False,
                 time_from=None,
                 time_to=None,
                 aggs: dict = None
                 ):
        self.query = None
        if query is not None:
            self.query = {"queryType": "string", "queryStr": query}
        if aggs is not None:
            self.aggregations = aggs

        self.disableHighlight = disable_highlight
        self.endId = end_id
        self.startId = start_id
        if table is None:
            table = "*"
        self.tableNames = [table]
        self.numResults = num
        self.fields = fields
        if self.fields == "*":
            self.fields = ["*"]

        self.timeRangeFilter = {
            "startTimeInSec": time_from,
            "endTimeInSec": time_to,
        }

        if not self.timeRangeFilter["startTimeInSec"] and not self.timeRangeFilter["endTimeInSec"]:
            now = int(time.time())
            self.timeRangeFilter["startTimeInSec"] = now - 15 * 60
            self.timeRangeFilter["endTimeInSec"] = now

        if table is None:
            self.table = []

    def to_dict(self):
        return dict((k, v) for k, v in self.__dict__.items() if v)
