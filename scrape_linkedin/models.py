from django.db import models

# Create your models here.

from django.db import models


class LinkedInUserModel(models.Model):
    user_id = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self) -> str:
        return self.user_id
    
class LinkedInPostModel(models.Model):
    post_id = models.CharField(max_length=255, blank=True, null=True)
    posting_user = models.OneToOneField(LinkedInUserModel, blank=True, null=True, on_delete=models.CASCADE)
    likes_count = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self) -> str:
        return f"{self.post_id}"

class linkedInPostLikeDetailsModel(models.Model):
    post = models.OneToOneField(LinkedInPostModel, blank=True, null=True, on_delete=models.CASCADE)
    liker = models.ForeignKey(LinkedInUserModel, blank=True, null=True, on_delete=models.CASCADE)
    
    
    def __str__(self) -> str:
        return self.post