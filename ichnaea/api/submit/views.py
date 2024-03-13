"""
Implementation of submit specific HTTP service views.
"""

import markus
from redis import RedisError

from ichnaea.api.exceptions import (
    ServiceUnavailable,
    UploadSuccess,
    UploadSuccessV0,
    Unauthorized,
)
from ichnaea.api.submit.schema_v0 import SUBMIT_V0_SCHEMA
from ichnaea.api.submit.schema_v1 import SUBMIT_V1_SCHEMA
from ichnaea.api.submit.schema_v2 import SUBMIT_V2_SCHEMA

from ichnaea.api.views import BaseAPIView


METRICS = markus.get_metrics()


class BaseSubmitView(BaseAPIView):
    """Common base class for all submit related views."""

    error_on_invalidkey = False
    view_type = "submit"
    success = UploadSuccess

    def __init__(self, request):
        super(BaseSubmitView, self).__init__(request)
        self.queue = self.request.registry.data_queues["update_incoming"]

    def emit_upload_metrics(self, value, api_key):
        tags = None
        if api_key.valid_key:
            tags = ["key:%s" % api_key.valid_key]
        METRICS.incr("data.batch.upload", tags=tags)

    def submit(self, api_key):
        raise self.prepare_exception(Unauthorized())
        # request_data = self.preprocess_request()

        # if not request_data:
        #     # don't allow completely empty request
        #     raise self.prepare_exception(ParseError())

        # if not api_key.store_sample("submit"):
        #     # only store some percentage of the requests
        #     return

        # valid_key = api_key.valid_key
        # data = []
        # for report in request_data["items"]:
        #     source = "gnss"
        #     if report is not None:
        #         position = report.get("position")
        #         if position is not None:
        #             source = position.get("source", "gnss")

        #     data.append({"api_key": valid_key, "report": report, "source": source})

        # self.queue.enqueue(data)
        # self.emit_upload_metrics(len(data), api_key)

    def view(self, api_key):
        """
        Execute the view code and return a response.
        """
        try:
            self.submit(api_key)
        except RedisError:
            raise self.prepare_exception(ServiceUnavailable())

        return self.prepare_exception(self.success())


class SubmitV0View(BaseSubmitView):
    """Submit version 0 view for `/v1/submit`."""

    metric_path = "v1.submit"
    route = "/v1/submit"
    schema = SUBMIT_V0_SCHEMA
    success = UploadSuccessV0


class SubmitV1View(BaseSubmitView):
    """Submit version 1 view for `/v1/geosubmit`."""

    metric_path = "v1.geosubmit"
    route = "/v1/geosubmit"
    schema = SUBMIT_V1_SCHEMA


class SubmitV2View(BaseSubmitView):
    """Submit version 2 view for `/v2/geosubmit`."""

    metric_path = "v2.geosubmit"
    route = "/v2/geosubmit"
    schema = SUBMIT_V2_SCHEMA
