from datetime import timedelta,datetime
from itertools import count 
import json

from django.utils import timezone
from django.db.models import Q

from rest_framework.views import APIView, Response
from common.models import County, SubCounty, Ward
from chul.models import CommunityHealthUnit
from users.models import MflUser

from ..models import (
    OwnerType,
    Owner,
    FacilityStatus,
    FacilityType,
    Facility,KephLevel
)
from ..views import QuerysetFilterMixin


class DashBoard(QuerysetFilterMixin, APIView):
    queryset = Facility.objects.all()
    
    def get_chu_count_in_county_summary(self, county):
        return CommunityHealthUnit.objects.filter(
            facility__ward__sub_county__county=county).count()

    def get_chu_count_in_constituency_summary(self, const):
        return CommunityHealthUnit.objects.filter(
            facility__ward__sub_county=const).count()

    def get_chu_count_in_ward_summary(self, ward):
        return CommunityHealthUnit.objects.filter(
            facility__ward=ward).count()

    def get_facility_county_summary(self,period_start,period_end):
        userlevel = self._get_user_top_level().get('userlevel', '')

        summary_array=[]
        allcounties=County.objects.all()
        for county in allcounties:
            userlevelfilters = {'created__gte': period_start, 'created__lte': period_end,
                                'county__id': county.id}
            if userlevel == 'county':
                userlevelfilters['county__id'] = self.request.user.county.id
            elif userlevel == 'sub_county':
                userlevelfilters['sub_county__id'] = self.request.user.sub_county.id

            queryset = Facility.objects.filter(**userlevelfilters);
            # get filters based on clients parameters
            parameterfilters = {}
            if self.request.query_params.get('ward'):
                parameterfilters['ward'] = self.request.query_params.get('ward')
            elif self.request.query_params.get('sub_county'):
                parameterfilters['sub_county'] = self.request.query_params.get('sub_county')
            elif self.request.query_params.get('county'):
                parameterfilters['county'] = self.request.query_params.get('county')

            queryset = queryset.filter(**parameterfilters)
            summary_array.append({county.name: queryset.count()})

        # Get the top ten locations
        top_ten_locations = sorted(summary_array, key=lambda x: list(x.values())[0], reverse=True)[:10]

        top_10_counties_summary = []
        for item in top_ten_locations:
            county = County.objects.get(name=item.keys()[0])
            chu_count = self.get_chu_count_in_county_summary(county)
            top_10_counties_summary.append(
                {
                    "name": item.keys()[0],
                    "count": item.values()[0],
                    "chu_count": chu_count
                })
        return top_10_counties_summary if self.request.user.is_national else []

    def get_facility_constituency_summary(self, period_start,period_end):
        userlevel = self._get_user_top_level().get('userlevel', '')

        summary_array = []
        allsubcounties = SubCounty.objects.all()
        for subcounty in allsubcounties:
            userlevelfilters = {'created__gte': period_start, 'created__lte': period_end,
                                'sub_county__id': subcounty.id}
            if userlevel == 'county':
                userlevelfilters['county__id'] = self.request.user.county.id
            elif userlevel == 'sub_county':
                userlevelfilters['sub_county__id'] = self.request.user.sub_county.id

            queryset = Facility.objects.filter(**userlevelfilters);
            # get filters based on clients parameters
            parameterfilters = {}
            if self.request.query_params.get('ward'):
                parameterfilters['ward'] = self.request.query_params.get('ward')
            elif self.request.query_params.get('sub_county'):
                parameterfilters['sub_county'] = self.request.query_params.get('sub_county')
            elif self.request.query_params.get('county'):
                parameterfilters['county'] = self.request.query_params.get('county')

            queryset = queryset.filter(**parameterfilters)
            summary_array.append({subcounty.name: queryset.count()})

        # Get the top ten locations
        top_ten_locations = sorted(summary_array, key=lambda x: list(x.values())[0], reverse=True)[:10]

        top_10_subcounties_summary = []
        for item in top_ten_locations:
            sub = SubCounty.objects.get(name=item.keys()[0])
            chu_count = self.get_chu_count_in_constituency_summary(sub)
            top_10_subcounties_summary.append(
                {
                    "name": item.keys()[0],
                    "count": item.values()[0],
                    "chu_count": chu_count
                })
        return top_10_subcounties_summary
        
    def get_facility_ward_summary(self,period_start,period_end):
        userlevel = self._get_user_top_level().get('userlevel', '')
        summary_array = []
        allwards = Ward.objects.all()
        for ward in allwards:
            userlevelfilters = {'created__gte': period_start, 'created__lte': period_end,
                                'ward__id': ward.id}
            if userlevel == 'county':
                userlevelfilters['county__id'] = self.request.user.county.id
            elif userlevel == 'sub_county':
                userlevelfilters['sub_county__id'] = self.request.user.sub_county.id

            queryset = Facility.objects.filter(**userlevelfilters);
            # get filters based on clients parameters
            parameterfilters = {}
            if self.request.query_params.get('ward'):
                parameterfilters['ward'] = self.request.query_params.get('ward')
            elif self.request.query_params.get('sub_county'):
                parameterfilters['sub_county'] = self.request.query_params.get('sub_county')
            elif self.request.query_params.get('county'):
                parameterfilters['county'] = self.request.query_params.get('county')

            queryset = queryset.filter(**parameterfilters)
            summary_array.append({str(ward.name + "|" + str(ward.code)): queryset.count()})

        top_10_wards = sorted(summary_array,key=lambda x: list(x.values())[0], reverse=True)[:10]
        top_10_wards_summary = []
        for item in top_10_wards:
            ward = Ward.objects.get(code=item.keys()[0].split('|')[1])
            chu_count = self.get_chu_count_in_ward_summary(ward)
            top_10_wards_summary.append(
                {
                    "name": item.keys()[0],
                    "count": item.values()[0],
                    "chu_count": chu_count
                })
        return top_10_wards_summary

    def get_facility_type_summary(self, cty, period_start,period_end):
        facility_type_parents_names = []
        for f_type in FacilityType.objects.all():
            if f_type.sub_division:
                facility_type_parents_names.append(f_type.sub_division)

        facility_types = FacilityType.objects.filter(
            sub_division__in=facility_type_parents_names)

        facility_type_summary = []
        summaries = {}
        for parent in facility_type_parents_names:
            summaries[parent] = 0

        for facility_type in facility_types:
            if self.request.query_params.get('ward'): 
                summaries[facility_type.sub_division] = self.get_queryset().filter(created__gte=period_start, created__lte=period_end,
                    facility_type=facility_type, ward=self.request.query_params.get('ward')).count()
            elif self.request.query_params.get('sub_county'):
                summaries[facility_type.sub_division] = self.get_queryset().filter(created__gte=period_start, created__lte=period_end,
                    facility_type=facility_type, sub_county=self.request.query_params.get('sub_county')).count()
            elif self.request.query_params.get('county'):
                 summaries[facility_type.sub_division] = self.get_queryset().filter(created__gte=period_start, created__lte=period_end,
                    facility_type=facility_type, county=self.request.query_params.get('county')).count()
            elif self.request.user.is_national:
                summaries[facility_type.sub_division] = summaries.get(
                        facility_type.sub_division) + self.get_queryset().filter(created__gte=period_start, created__lte=period_end,
                                facility_type=facility_type).count()
            else:
                if(self.mfluser.user_groups.get('is_sub_county_level')):
                    summaries[facility_type.sub_division] = self.get_queryset().filter(created__gte=period_start, created__lte=period_end,
                    facility_type=facility_type, sub_county=self.usersubcounty).count()
                elif(self.mfluser.user_groups.get('is_county_level')):
                    summaries[facility_type.sub_division] = self.get_queryset().filter(created__gte=period_start, created__lte=period_end,
                    facility_type=facility_type, county=self.usercounty).count()
                else:
                    summaries[facility_type.sub_division] =0
        
        facility_type_summary =  [
            {"name": key, "count": value } for key, value in summaries.items()
        ]

        facility_type_summary_sorted = sorted(
            facility_type_summary,
            key=lambda x: x, reverse=True)

        return facility_type_summary_sorted

    def get_facility_owner_summary(self, cty, period_start,period_end):
        userlevel = self._get_user_top_level().get('userlevel', '')
        allowners = Owner.objects.all()
        summary_array = []
        for owner in allowners:
            userlevelfilters = {'created__gte': period_start, 'created__lte': period_end,
                                'owner__id': owner.id}
            if userlevel == 'county':
                userlevelfilters['county__id'] = self.request.user.county.id
            elif userlevel == 'sub_county':
                userlevelfilters['sub_county__id'] = self.request.user.sub_county.id

            queryset = self.get_queryset().filter(**userlevelfilters);
            # get filters based on clients parameters
            parameterfilters = {}
            if self.request.query_params.get('ward'):
                parameterfilters['ward'] = self.request.query_params.get('ward')
            elif self.request.query_params.get('sub_county'):
                parameterfilters['sub_county'] = self.request.query_params.get('sub_county')
            elif self.request.query_params.get('county'):
                parameterfilters['county'] = self.request.query_params.get('county')

            queryset = queryset.filter(**parameterfilters)
            summary_array.append({'name':owner.name,'count': queryset.count()})

        return summary_array

    def get_facility_status_summary(self, cty, period_start,period_end):
        userlevel = self._get_user_top_level().get('userlevel', '')
        summary_array = []
        allstatus = FacilityStatus.objects.all()
        for status in allstatus:
            userlevelfilters = {'created__gte': period_start, 'created__lte': period_end,
                                'operation_status': status.id}
            if userlevel == 'county':
                userlevelfilters['county__id'] = self.request.user.county.id
            elif userlevel == 'sub_county':
                userlevelfilters['sub_county__id'] = self.request.user.sub_county.id

            queryset = self.get_queryset().filter(**userlevelfilters);
            # get filters based on clients parameters
            parameterfilters = {}
            if self.request.query_params.get('ward'):
                parameterfilters['ward'] = self.request.query_params.get('ward')
            elif self.request.query_params.get('sub_county'):
                parameterfilters['sub_county'] = self.request.query_params.get('sub_county')
            elif self.request.query_params.get('county'):
                parameterfilters['county'] = self.request.query_params.get('county')

            queryset = queryset.filter(**parameterfilters)
            summary_array.append({status.name : queryset.count()})


        return summary_array

    def get_facility_owner_types_summary(self, cty, period_start,period_end):
        userlevel = self._get_user_top_level().get('userlevel', '')
        summary_array = []
        allownertypes = OwnerType.objects.all()
        for owner in allownertypes:
            userlevelfilters = {'created__gte': period_start, 'created__lte': period_end,
                                'owner__owner_type__id': owner.id}
            if userlevel == 'county':
                userlevelfilters['county__id'] = self.request.user.county.id
            elif userlevel == 'sub_county':
                userlevelfilters['sub_county__id'] = self.request.user.sub_county.id

            queryset = Facility.objects.filter(**userlevelfilters)
            # get filters based on clients parameters
            parameterfilters = {}
            if self.request.query_params.get('ward'):
                parameterfilters['ward'] = self.request.query_params.get('ward')
            elif self.request.query_params.get('sub_county'):
                parameterfilters['sub_county'] = self.request.query_params.get('sub_county')
            elif self.request.query_params.get('county'):
                parameterfilters['county'] = self.request.query_params.get('county')

            queryset = queryset.filter(**parameterfilters)
            summary_array.append({'name':owner.name,'count': queryset.count()})

        return summary_array

    def get_recently_created_facilities(self, cty, period_start,period_end):
      
        if self.request.query_params.get('ward'): 
            return self.get_queryset().filter(created__gte=period_start, created__lte=period_end,ward=self.request.query_params.get('ward')).count()
        elif self.request.query_params.get('sub_county'):
            return self.get_queryset().filter(created__gte=period_start, created__lte=period_end,sub_county=self.request.query_params.get('sub_county')).count()
        elif self.request.query_params.get('county'):
            return self.get_queryset().filter(created__gte=period_start, created__lte=period_end,county=self.request.query_params.get('county')).count()
        elif self.request.user.is_national:
            return self.get_queryset().filter(created__gte=period_start, created__lte=period_end).count()
        else:
            if(self.mfluser.user_groups.get('is_sub_county_level')):
                return self.get_queryset().filter(created__gte=period_start, created__lte=period_end,sub_county=self.usersubcounty).count()
            elif(self.mfluser.user_groups.get('is_county_level')):
                return self.get_queryset().filter(created__gte=period_start, created__lte=period_end,county=self.usercounty).count()
            else:
                return 0
    
    def get_recently_updated_facilities(self, cty, period_start,period_end):
      
        if self.request.query_params.get('ward'): 
            return self.get_queryset().filter(updated__gte=period_start, updated__lte=period_end,ward=self.request.query_params.get('ward')).count()
        elif self.request.query_params.get('sub_county'):
            return self.get_queryset().filter(updated__gte=period_start, updated__lte=period_end,sub_county=self.request.query_params.get('sub_county')).count()
        elif self.request.query_params.get('county'):
            return self.get_queryset().filter(updated__gte=period_start, updated__lte=period_end,county=self.request.query_params.get('county')).count()
        elif self.request.user.is_national:
            return self.get_queryset().filter(updated__gte=period_start, updated__lte=period_end).count()
        else:
            if(self.mfluser.user_groups.get('is_sub_county_level')):
                return self.get_queryset().filter(updated__gte=period_start, updated__lte=period_end,sub_county=self.usersubcounty).count()
            elif(self.mfluser.user_groups.get('is_county_level')):
                return self.get_queryset().filter(updated__gte=period_start, updated__lte=period_end,county=self.usercounty).count()
            else:
                return 0

    def get_recently_created_chus(self, cty, period_start,period_end):

        if self.request.query_params.get('ward'): 
                return CommunityHealthUnit.objects.filter(created__gte=period_start, created__lte=period_end,facility__ward=self.request.query_params.get('ward'),facility__in=self.get_queryset()).count()
        elif self.request.query_params.get('sub_county'):
                return CommunityHealthUnit.objects.filter(created__gte=period_start, created__lte=period_end,facility__ward__sub_county= self.request.query_params.get('sub_county'),facility__in=self.get_queryset()).count()
        elif self.request.query_params.get('county'):
                return CommunityHealthUnit.objects.filter(created__gte=period_start, created__lte=period_end,facility__ward__sub_county__county=self.request.query_params.get('county'),facility__in=self.get_queryset()).count()
        elif self.request.user.is_national:
            return self.get_queryset().filter(created__gte=period_start, created__lte=period_end).count()
        else:
            if(self.mfluser.user_groups.get('is_sub_county_level')):
                return CommunityHealthUnit.objects.filter(created__gte=period_start, created__lte=period_end,facility__ward__sub_county=self.usersubcounty,facility__in=self.get_queryset()).count()
            elif(self.mfluser.user_groups.get('is_county_level')):
                return CommunityHealthUnit.objects.filter(created__gte=period_start, created__lte=period_end,facility__ward__sub_county__county=self.usercounty,facility__in=self.get_queryset()).count()
            else:
                return 0
        
    def get_recently_updated_chus(self, cty, period_start,period_end):

        if self.request.query_params.get('ward'): 
                return CommunityHealthUnit.objects.filter(updated__gte=period_start, updated__lte=period_end,facility__ward=self.request.query_params.get('ward'),facility__in=self.get_queryset()).count()
        elif self.request.query_params.get('sub_county'):
                return CommunityHealthUnit.objects.filter(updated__gte=period_start, updated__lte=period_end,facility__ward__sub_county= self.request.query_params.get('sub_county'),facility__in=self.get_queryset()).count()
        elif self.request.query_params.get('county'):
                return CommunityHealthUnit.objects.filter(updated__gte=period_start, updated__lte=period_end,facility__ward__sub_county__county=self.request.query_params.get('county'),facility__in=self.get_queryset()).count()
        elif self.request.user.is_national:
            return self.get_queryset().filter(updated__gte=period_start, updated__lte=period_end).count()
        else:
            if(self.mfluser.user_groups.get('is_sub_county_level')):
                return CommunityHealthUnit.objects.filter(updated__gte=period_start, updated__lte=period_end,facility__ward__sub_county=self.usersubcounty,facility__in=self.get_queryset()).count()
            elif(self.mfluser.user_groups.get('is_county_level')):
                return CommunityHealthUnit.objects.filter(updated__gte=period_start, updated__lte=period_end,facility__ward__sub_county__county=self.usercounty,facility__in=self.get_queryset()).count()
            else:
                return 0
        
    def facilities_pending_approval_count(self, cty, period_start,period_end):
        userlevel = self._get_user_top_level().get('userlevel', '')
        userlevelfilters = {}
        if userlevel == 'county':
            userlevelfilters['county__id'] = self.request.user.county.id
        elif userlevel == 'sub_county':
            userlevelfilters['sub_county__id'] = self.request.user.sub_county.id

        myqueryset = self.get_queryset().filter(**userlevelfilters)

        parameterfilters = {}
        if self.request.query_params.get('ward'):
            parameterfilters['ward'] = self.request.query_params.get('ward')
        elif self.request.query_params.get('sub_county'):
            parameterfilters['sub_county'] = self.request.query_params.get('sub_county')
        elif self.request.query_params.get('county'):
            parameterfilters['county'] = self.request.query_params.get('county')

        queryset = myqueryset.filter(**parameterfilters)
        updated_pending_approval = queryset.filter(has_edits=True)
        newly_created = queryset.filter(approved=False,rejected=False)

        return len(
            list(set(list(updated_pending_approval) + list(newly_created)))
        )
   
    def get_facilities_approved_count(self,cty,period_start,period_end):
        userlevel = self._get_user_top_level().get('userlevel', '')
        userlevelfilters = {'approved': True, 'rejected': False}
        if userlevel == 'county':
            userlevelfilters['county__id'] = self.request.user.county.id
        elif userlevel == 'sub_county':
            userlevelfilters['sub_county__id'] = self.request.user.sub_county.id

        myqueryset = self.get_queryset().filter(**userlevelfilters)

        parameterfilters = {}
        if self.request.query_params.get('ward'):
            parameterfilters['ward'] = self.request.query_params.get('ward')
        elif self.request.query_params.get('sub_county'):
            parameterfilters['sub_county'] = self.request.query_params.get('sub_county')
        elif self.request.query_params.get('county'):
            parameterfilters['county'] = self.request.query_params.get('county')
        queryset = myqueryset.filter(**parameterfilters)
        return  queryset.count()

    def get_chus_pending_approval(self, cty,period_start,period_end):
        """
        Get the number of CHUs pending approval
        """
        if self.request.query_params.get('ward'): 
            return CommunityHealthUnit.objects.filter(created__gte=period_start, created__lte=period_end).filter(
                    Q(is_approved=False, is_rejected=False) |
                    Q(has_edits=True)).distinct().filter(
                        facility__in=self.get_queryset(),
                        facility__ward=self.request.query_params.get('ward')).count()
        elif self.request.query_params.get('sub_county'):
            return CommunityHealthUnit.objects.filter(created__gte=period_start, created__lte=period_end).filter(
                    Q(is_approved=False, is_rejected=False) |
                    Q(has_edits=True)).distinct().filter(
                        facility__in=self.get_queryset(), facility__sub_county=self.request.query_params.get('sub_county')).count()
        elif self.request.query_params.get('county'):
            return CommunityHealthUnit.objects.filter(created__gte=period_start, created__lte=period_end).filter(
                    Q(is_approved=False, is_rejected=False) |
                    Q(has_edits=True)).distinct().filter(
                        facility__in=self.get_queryset(), facility__county=self.usercounty).count()
        elif self.request.user.is_national:
            return CommunityHealthUnit.objects.filter(created__gte=period_start, created__lte=period_end).filter(
                Q(is_approved=False, is_rejected=False) |
                Q(has_edits=True)).distinct().filter(
                    facility__in=self.get_queryset()).count()
        else:
            if(self.mfluser.user_groups.get('is_sub_county_level')):
                return CommunityHealthUnit.objects.filter(created__gte=period_start, created__lte=period_end).filter(
                    Q(is_approved=False, is_rejected=False) |
                    Q(has_edits=True)).distinct().filter(
                        facility__in=self.get_queryset(), facility__sub_county=self.usersubcounty).count()
            elif(self.mfluser.user_groups.get('is_county_level')):
                return CommunityHealthUnit.objects.filter(created__gte=period_start, created__lte=period_end).filter(
                    Q(is_approved=False, is_rejected=False) |
                    Q(has_edits=True)).distinct().filter(
                        facility__in=self.get_queryset(), facility__county=self.usercounty).count()
            else:
                return 0

    def get_rejected_chus(self, cty,period_start,period_end):
        """
        Get the number of CHUs that have been rejected
        """
        if self.request.query_params.get('ward'): 
            return CommunityHealthUnit.objects.filter(
                    is_rejected=True, approval_date__gte=period_start, approval_date__lte=period_end,
                    facility__ward=self.request.query_params.get('ward')).count()
        elif self.request.query_params.get('sub_county'):
            return CommunityHealthUnit.objects.filter(
                    is_rejected=True,approval_date__gte=period_start, approval_date__lte=period_end,
                    facility__sub_county=self.request.query_params.get('sub_county')).count()
        elif self.request.query_params.get('county'):
            return CommunityHealthUnit.objects.filter(
                    is_rejected=True, approval_date__gte=period_start, approval_date__lte=period_end,
                    facility__county=self.request.query_params.get('county')).count()
        elif self.request.user.is_national:
            return CommunityHealthUnit.objects.filter(approval_date__gte=period_start, approval_date__lte=period_end, is_rejected=True).count()
        else:
            if(self.mfluser.user_groups.get('is_sub_county_level')):
                return CommunityHealthUnit.objects.filter(
                    is_rejected=True,approval_date__gte=period_start, approval_date__lte=period_end,
                    facility__sub_county=self.usersubcounty).count()
            elif(self.mfluser.user_groups.get('is_county_level')):
                return CommunityHealthUnit.objects.filter(
                    is_rejected=True,approval_date__gte=period_start, approval_date__lte=period_end,
                    facility__county=self.usercounty).count()
            else:
                return 0
  

    def get_rejected_facilities_count(self, cty, period_start,period_end):
        userlevel = self._get_user_top_level().get('userlevel', '')
        userlevelfilters = {'rejected': True }
        if userlevel == 'county':
            userlevelfilters['county__id'] = self.request.user.county.id
        elif userlevel == 'sub_county':
            userlevelfilters['sub_county__id'] = self.request.user.sub_county.id

        myqueryset = self.get_queryset().filter(**userlevelfilters)

        parameterfilters = {}
        if self.request.query_params.get('ward'):
            parameterfilters['ward'] = self.request.query_params.get('ward')
        elif self.request.query_params.get('sub_county'):
            parameterfilters['sub_county'] = self.request.query_params.get('sub_county')
        elif self.request.query_params.get('county'):
            parameterfilters['county'] = self.request.query_params.get('county')
        queryset = myqueryset.filter(**parameterfilters)
        return queryset.count()

    def get_closed_facilities_count(self, cty, period_start,period_end):
        userlevel = self._get_user_top_level().get('userlevel', '')
        userlevelfilters = {'closed': True,'closed_date__gte':period_start ,'closed_date__lte':period_end}
        if userlevel == 'county':
            userlevelfilters['county__id'] = self.request.user.county.id
        elif userlevel == 'sub_county':
            userlevelfilters['sub_county__id'] = self.request.user.sub_county.id

        myqueryset = self.get_queryset().filter(**userlevelfilters)

        parameterfilters = {}
        if self.request.query_params.get('ward'):
            parameterfilters['ward'] = self.request.query_params.get('ward')
        elif self.request.query_params.get('sub_county'):
            parameterfilters['sub_county'] = self.request.query_params.get('sub_county')
        elif self.request.query_params.get('county'):
            parameterfilters['county'] = self.request.query_params.get('county')
        queryset = myqueryset.filter(**parameterfilters)

        return queryset.count()


        
    def get_facilities_kephlevel_count(self,county_name,period_start,period_end):
        """
        Function to get facilities by keph level
        """
        userlevel = self._get_user_top_level().get('userlevel', '')
        keph_level = KephLevel.objects.values("id", "name")  
        keph_array = []
        for keph in keph_level:
            userlevelfilters={'created__gte':period_start, 'created__lte':period_end, 'keph_level_id':keph.get("id")}
            if userlevel=='county':
                userlevelfilters['county__id']= self.request.user.county.id
            elif userlevel=='sub_county':
                userlevelfilters['sub_county__id']= self.request.user.sub_county.id

            queryset=Facility.objects.filter(**userlevelfilters);
            # get filters based on clients parameters
            parameterfilters = {}
            if self.request.query_params.get('ward'):
                parameterfilters['ward'] = self.request.query_params.get('ward')
            elif self.request.query_params.get('sub_county'):
                parameterfilters['sub_county'] = self.request.query_params.get('sub_county')
            elif self.request.query_params.get('county'):
                parameterfilters['county'] = self.request.query_params.get('county')

            queryset=queryset.filter(**parameterfilters)
            keph_array.append({"name": keph.get("name"), "count": queryset.count()})

        return keph_array


    def _get_user_top_level(self):
        userid = self.request.user.groups.all()[0].id
        resultobject = {'userlevel': ''}
        if userid == 5 or userid == 6 or userid == 7:
            resultobject['userlevel'] = 'national'
        elif userid == 1 or userid == 12:
            resultobject['userlevel'] = 'county'
        elif userid == 2:
            resultobject['userlevel'] = 'sub_county'
        else:
            resultobject['userlevel'] = 'sub_county'

        return resultobject

    def get(self, *args, **kwargs):
        
        user = self.request.user 
        county_ = user.county  
        muser=MflUser.objects.filter(id=user.id)[0]
        self.mfluser=muser
        self.usercounty=muser.countyid
        self.usersubcounty=muser.sub_countyid
        period_start = self.request.query_params.get('datefrom')
        period_end = self.request.query_params.get('dateto') 
        if not period_end:
            period_end=datetime.max
        if not period_start:
            period_start=datetime.min 
        
    
        #get total facilities
        if self.request.query_params.get('ward'): 
            total_facilities = self.get_queryset().filter(created__gte=period_start, created__lte=period_end, ward=self.request.query_params.get('ward')).count()
        elif self.request.query_params.get('sub_county'):
            total_facilities = self.get_queryset().filter(created__gte=period_start, created__lte=period_end, sub_county=self.request.query_params.get('sub_county')).count()
        elif self.request.query_params.get('county'):
            total_facilities = self.get_queryset().filter(created__gte=period_start, created__lte=period_end,county=self.request.query_params.get('county')).count() 
        elif self.request.user.is_national:
            total_facilities = self.queryset.filter(created__gte=period_start, created__lte=period_end).count()
        else:
            userlevel=self._get_user_top_level().get('userlevel','')
            if userlevel == 'national':
                total_facilities = self.get_queryset().filter(created__gte=period_start, created__lte=period_end).count()
            elif userlevel == 'sub_county':
                total_facilities = self.get_queryset().filter(created__gte=period_start, created__lte=period_end, sub_county=self.usersubcounty).count()
            elif userlevel == 'county':
                total_facilities = self.get_queryset().filter(created__gte=period_start, created__lte=period_end,county=self.usercounty).count() 
            else:
                total_facilities=0
        
        #get total chus
        if self.request.query_params.get('ward'):
            total_chus = CommunityHealthUnit.objects.filter(date_established__gte=period_start, date_established__lte=period_end).filter(
                    facility__in=self.get_queryset().filter(ward=self.request.query_params.get('ward'))).count()
        elif self.request.query_params.get('sub_county'):
            total_chus = CommunityHealthUnit.objects.filter(date_established__gte=period_start, date_established__lte=period_end).filter(
                    facility__in=self.get_queryset().filter(sub_county=self.request.query_params.get('sub_county'))).count()
        elif self.request.query_params.get('county'):
            total_chus = CommunityHealthUnit.objects.filter(date_established__gte=period_start, date_established__lte=period_end).filter(
                    facility__in=self.get_queryset().filter(county=self.request.query_params.get('county'))).count()
        elif self.request.user.is_national:
            total_chus = CommunityHealthUnit.objects.filter(date_established__gte=period_start, date_established__lte=period_end).filter(facility__in=self.get_queryset()).count()
        else:
            if(self.mfluser.user_groups.get('is_sub_county_level')):
                total_chus = CommunityHealthUnit.objects.filter(date_established__gte=period_start, date_established__lte=period_end).filter(
                    facility__in=self.get_queryset().filter(sub_county=self.request.query_params.get('sub_county'))).count()
            elif(self.mfluser.user_groups.get('is_county_level')):
                total_chus = CommunityHealthUnit.objects.filter(date_established__gte=period_start, date_established__lte=period_end).filter(
                    facility__in=self.get_queryset().filter(county=self.request.query_params.get('county'))).count()
            else:
                total_chus=0
        

        #return data
        data = {
            "timeperiod":[{"startdate":period_start},{"enddate":period_end}],
            "keph_level" : self.get_facilities_kephlevel_count(county_,period_start,period_end),
            "total_facilities": total_facilities,
            "county_summary": self.get_facility_county_summary(period_start,period_end) if user.is_national else [],
            "constituencies_summary": self.get_facility_constituency_summary(period_start,period_end),
            # if user.county and not user.sub_county else [],
            "wards_summary": self.get_facility_ward_summary(period_start,period_end),
            # if user.sub_county else [],
            "owners_summary": self.get_facility_owner_summary(county_,period_start,period_end),
            "types_summary": self.get_facility_type_summary(county_,period_start,period_end),
            "status_summary": self.get_facility_status_summary(county_,period_start,period_end),
            "owner_types": self.get_facility_owner_types_summary(county_,period_start,period_end),
            "recently_created": self.get_recently_created_facilities(county_,period_start,period_end),
            "recently_updated": self.get_recently_updated_facilities(county_,period_start,period_end),
            "recently_created_chus": self.get_recently_created_chus(county_,period_start,period_end),
            "recently_updated_chus": self.get_recently_updated_chus(county_,period_start,period_end),
            "pending_updates": self.facilities_pending_approval_count(county_,period_start,period_end),
            "rejected_facilities_count": self.get_rejected_facilities_count(county_,period_start,period_end),
            "closed_facilities_count": self.get_closed_facilities_count(county_,period_start,period_end),
            "rejected_chus": self.get_rejected_chus(county_,period_start,period_end),
            "chus_pending_approval": self.get_chus_pending_approval(county_,period_start,period_end),
            "total_chus": total_chus,
            "approved_facilities": self.get_facilities_approved_count(county_,period_start,period_end),

        }

        fields = self.request.query_params.get("fields", None)
       
        if fields:
            required = fields.split(",")
            required_data = {
                i: data[i] for i in data if i in required
            }
            return Response(required_data)
        return Response(data)

#facility_county_summary
# if self.request.query_params.get('ward'): 
# elif self.request.query_params.get('sub_county'):
# elif self.request.query_params.get('county'):
# elif self.request.user.is_national:
# else:
#     if(self.mfluser.user_groups.get('is_sub_county_level')):
#     elif(self.mfluser.user_groups.get('is_county_level')):
#     else:

#keph level, recently_created_chus,recently_created