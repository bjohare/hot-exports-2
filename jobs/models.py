from __future__ import unicode_literals
import uuid
#from django.db import models
from django.contrib.gis.db import models
from django.utils import timezone
from django.contrib.auth.models import User, Group
from django.db.models.fields import CharField

class LowerCaseCharField(CharField):
    """
    Defines a charfield which automatically converts all inputs to
    lowercase and saves.
    """

    def pre_save(self, model_instance, add):
        """
        Converts the string to lowercase before saving.
        """
        current_value = getattr(model_instance, self.attname)
        setattr(model_instance, self.attname, current_value.lower())
        return getattr(model_instance, self.attname)


class TimeStampedModelMixin(models.Model):
    """
    Mixin for timestamped models.
    """
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now, editable=False)
    
    class Meta:
        abstract = True


class ExportFormat(TimeStampedModelMixin):
    """Model for a ExportFormat"""
    id = models.AutoField(primary_key=True, editable=False)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, db_index=True)
    name = models.CharField(max_length=100)
    slug = LowerCaseCharField(max_length=7, unique=True, default='')    
    description = models.CharField(max_length=255)
    cmd = models.TextField(max_length=1000)
    objects = models.Manager()
    
    class Meta:
        managed = True
        db_table = 'export_formats'
        
    def __str__(self):
        return '{0}'.format(self.name)
    
    def __unicode__(self, ):
        return '{0}'.format(self.slug)
    

class Job(TimeStampedModelMixin):
    """
    Model for a Job.
    """
    id = models.AutoField(primary_key=True, editable=False)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, db_index=True)
    user = models.ForeignKey(User, related_name='user')
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    status = models.CharField(max_length=30)
    formats = models.ManyToManyField(ExportFormat, related_name='formats')
    the_geom = models.PolygonField(verbose_name='Extent for export', srid=4326, default='')
    the_geom_webmercator = models.PolygonField(verbose_name='Mercator extent for export', srid=3857, default='')
    the_geog = models.PolygonField(verbose_name='Geographic extent for export', geography=True, default='') # create geog column
    objects = models.GeoManager()
    
    class Meta:
        managed = True
        db_table = 'jobs'
        
    def __str__(self):
        return '{0}'.format(self.name)
    
    
class ExportTask(TimeStampedModelMixin):
    """
    Model for an ExportTask.
    """
    id = models.AutoField(primary_key=True, editable=False)
    uid = models.UUIDField(blank=True) # celery task id
    job = models.ForeignKey(Job, related_name='job')
    

class Region(TimeStampedModelMixin):
    """
    Model for a HOT Export Region.
    """
    id = models.AutoField(primary_key=True, editable=False)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, db_index=True)
    description = models.CharField(max_length=1000, blank=True)
    the_geom = models.PolygonField(verbose_name='HOT Export Region', srid=4326, default='')
    the_geom_webmercator = models.PolygonField(verbose_name='Mercator extent for export region', srid=3857, default='')
    the_geog = models.PolygonField(verbose_name='Geographic extent for export region', geography=True, default='') 
    objects = models.GeoManager()
    
    class Meta:
        managed = True
        db_table = 'regions'
    
    def __str__(self):
        return '{0}'.format(self.name)
    
    def save(self, *args, **kwargs):
        # pull out the_geom and update other spatial fields
        wkt = self.the_geom.wkt
        super(Region, self).save(*args, **kwargs)
