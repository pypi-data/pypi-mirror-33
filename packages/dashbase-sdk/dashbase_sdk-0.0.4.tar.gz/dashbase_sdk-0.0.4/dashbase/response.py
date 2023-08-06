from schematics.models import Model
from schematics.types.base import StringType, BooleanType, BaseType, LongType, FloatType
from schematics.types.compound import ListType, ModelType, DictType
from dashbase.request import Request


class HighlightIndex(Model):
    offset = LongType()
    length = LongType()


class HighlightEntity(Model):
    fields = DictType(ListType(ListType(ModelType(HighlightIndex))))  # type: dict[str, list[HighlightIndex]]
    stored = ListType(ModelType(HighlightIndex))  # type: list[HighlightIndex]


class Entity(Model):
    highlight = ModelType(HighlightEntity, default=None)  # type: HighlightIndex

    def is_highlight_entity(self):
        return self.highlight is not None


class Payload(Model):
    fields = DictType(ListType(StringType))
    stored = StringType()
    entities = ListType(ModelType(Entity))  # type: Entity


class Hit(Model):
    timeInSeconds = LongType()
    globalId = LongType()
    payload = ModelType(Payload)  # type: Payload


class DashbaseResponse(Model):
    raw_res = BaseType()


class Response(DashbaseResponse):
    request = ModelType(Request)  # type: Request
    totalDocs = LongType()
    numDocs = LongType()
    numHits = LongType()
    numDocsProcessed = LongType()
    numHitsProcessed = LongType()
    latencyInMillis = LongType()
    timeProcessedTo = LongType(default=0)
    isTimedOut = BooleanType(default=False)
    startId = StringType()
    endId = StringType()
    error = StringType()
    debugMap = DictType(BaseType)
    hits = ListType(ModelType(Hit))  # type: list[Hit]
    aggregations = DictType(BaseType)
    schema = DictType(StringType)


class SystemMetric(Model):
    cpuLoadFactor = FloatType()
    cpuUsagePercent = FloatType()
    numCores = LongType()
    heapUsage = LongType()
    heapUsagePercent = FloatType()
    diskUsage = LongType()
    diskUsagePercent = FloatType()


class IndexMetric(Model):
    numBytesPerSecond = LongType()
    numBytesPerDay = LongType()
    numEventsPerSecond = LongType()
    numEventsPerDay = LongType()


class QueryMetric(Model):
    avgLatencyMillis = LongType()
    minLatencyMillis = LongType()
    maxLatencyMillis = LongType()
    p99LatencyMillis = LongType()
    medianLatencyMillis = LongType()
    queriesPerSecond = LongType()


class ClusterMetricInfo(Model):
    system = ModelType(SystemMetric)  # type: SystemMetric
    indexing = ModelType(IndexMetric)  # type: IndexMetric
    query = ModelType(QueryMetric)  # type: QueryMetric
    isError = BooleanType()


class ClusterInfo(Model):
    metrics = ModelType(ClusterMetricInfo)  # type: ClusterMetricInfo
    info = DictType(ListType(StringType()))


class ClusterOverviewResponse(DashbaseResponse):
    clusterPrefix = StringType()
    overview = DictType(ModelType(ClusterInfo))  # type: dict[str, ClusterInfo]


class InfoResponse(DashbaseResponse):
    config = BaseType()
    schema = DictType(StringType)
    subtableInfo = DictType(LongType)
    numDocs = LongType()
    totalRawSize = LongType()
    totalIndexSize = LongType()
    totalPayloadSize = LongType()


class QueryResponse(object):
    def __init__(self, raw):
        self._parsed = False
        self.raw = raw
        self.hits = []
        self.end_id = None
        self.start_id = None
        self.num_hits = -1
        self.total_docs = -1
        self.aggregations = {}

    def parse(self):
        self.num_hits = self.raw['numHits']
        self.total_docs = self.raw['totalDocs']
        for hit in self.raw['hits']:
            obj = {
                '@timestamp': hit['timeInSeconds']
            }
            for key, value in hit["payload"]["fields"].items():
                obj[key] = value[0]
            self.hits.append(obj)
        if "startId" in self.raw:
            self.start_id = self.raw["startId"]

        if "endId" in self.raw:
            self.end_id = self.raw["endId"]

        self.aggregations = self.raw["aggregations"]
        self._parsed = True
