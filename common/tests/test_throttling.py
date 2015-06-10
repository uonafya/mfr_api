import json

from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase
from model_mommy import mommy

from facilities.models import FacilityService
from ..models import County
from ..serializers import CountySerializer
from .test_views import LoginMixin, default


class TestThrottling(LoginMixin, APITestCase):
    def test_non_throttled_view(self):
        # the counties view is not throttled:
        url = reverse('api:common:counties_list')
        county = mommy.make(County)
        response = self.client.get(url)
        self.assertEquals(200, response.status_code)
        expected_data = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                CountySerializer(county).data
            ]
        }
        self.assertEquals(
            json.loads(json.dumps(response.data, default=default)),
            json.loads(json.dumps(expected_data, default=default)))
        # call the url again to confirm it returns
        # throttle rate is once per day
        response_2 = self.client.get(url)
        self.assertEquals(200, response_2.status_code)
        self.assertEquals(
            json.loads(json.dumps(response_2.data, default=default)),
            json.loads(json.dumps(expected_data, default=default)))

    def test_throttled_view(self):
        # facility rating is throttled to once per day
        url = reverse("api:facilities:facility_service_ratings_list")
        fs = mommy.make(FacilityService)

        data = {
            "rating": 1,
            "facility_service": fs.id
        }
        response = self.client.post(
            path=url, data=data, REMOTE_ADDR="127.0.0.1")
        self.assertEquals(201, response.status_code)

        # the url for our current ip should not be throttled
        # after accessing it the first time

        data_2 = {
            "rating": 5,
            "facility_service": fs.id
        }

        response_2 = self.client.post(
            path=url, data=data_2, REMOTE_ADDR="127.0.0.1")
        self.assertEquals(429, response_2.status_code)