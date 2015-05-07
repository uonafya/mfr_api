from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from common.serializers import AbstractFieldsMixin
from .models import (
    GeoCodeSource,
    GeoCodeMethod,
    FacilityCoordinates,
    WorldBorder,
    CountyBoundary,
    ConstituencyBoundary,
    WardBoundary
)


class GeoCodeSourceSerializer(
        AbstractFieldsMixin, serializers.ModelSerializer):
    class Meta(object):
        model = GeoCodeSource


class GeoCodeMethodSerializer(
        AbstractFieldsMixin, serializers.ModelSerializer):
    class Meta(object):
        model = GeoCodeMethod


class FacilityCoordinatesSerializer(
        AbstractFieldsMixin, GeoFeatureModelSerializer):
    class Meta(object):
        model = FacilityCoordinates
        geo_field = "coordinates"


class AbstractBoundarySerializer(
        AbstractFieldsMixin, GeoFeatureModelSerializer):
    center = serializers.ReadOnlyField()
    facility_count = serializers.ReadOnlyField()
    density = serializers.ReadOnlyField()

    class Meta(object):
        geo_field = 'mpoly'


class WorldBorderSerializer(AbstractBoundarySerializer):
    center = serializers.ReadOnlyField()

    class Meta(AbstractBoundarySerializer.Meta):
        model = WorldBorder


class WorldBorderDetailSerializer(AbstractBoundarySerializer):
    facility_coordinates = serializers.ReadOnlyField()
    center = serializers.ReadOnlyField()

    class Meta(AbstractBoundarySerializer.Meta):
        model = WorldBorder


class CountyBoundarySerializer(AbstractBoundarySerializer):
    class Meta(AbstractBoundarySerializer.Meta):
        model = CountyBoundary


class CountyBoundaryDetailSerializer(AbstractBoundarySerializer):
    facility_coordinates = serializers.ReadOnlyField()

    class Meta(AbstractBoundarySerializer.Meta):
        model = CountyBoundary


class ConstituencyBoundarySerializer(AbstractBoundarySerializer):
    class Meta(AbstractBoundarySerializer.Meta):
        model = ConstituencyBoundary


class ConstituencyBoundaryDetailSerializer(AbstractBoundarySerializer):
    facility_coordinates = serializers.ReadOnlyField()

    class Meta(AbstractBoundarySerializer.Meta):
        model = ConstituencyBoundary


class WardBoundarySerializer(AbstractBoundarySerializer):
    class Meta(AbstractBoundarySerializer.Meta):
        model = WardBoundary


class WardBoundaryDetailSerializer(AbstractBoundarySerializer):
    facility_coordinates = serializers.ReadOnlyField()

    class Meta(AbstractBoundarySerializer.Meta):
        model = WardBoundary
