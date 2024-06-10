
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.viewsets import GenericViewSet
from .models import LinkedInPostModel
from .utils import get_linkedin_data


class DataScraperView(GenericViewSet):
    
    @action(methods=['GET'], detail=False)
    def scrap_user_data(self, request):
        user_id = self.request.query_params.get('user_id', '')
        if not user_id:
            return Response('Please add a username')
        
        result = get_linkedin_data(user_id)
        
        return Response(result)


    @action(methods=['GET'], detail=False)
    def get_current_db_data(self, request):
        all_data = DataSerializer(LinkedInPostModel.objects.all(), many=True).data
        return Response({"details":all_data})


class DataSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = LinkedInPostModel
        fields = '__all__'
