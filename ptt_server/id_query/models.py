from __future__ import unicode_literals

from django.db import models


# Create your models here.
class UserWordFreq(models.Model):
    user = models.CharField(u'User', max_length=50, null=True)

    def __unicode__(self):
        return self.user

# Create your models here.
class WordFreq(models.Model):
    word = models.TextField(u'Word', null=True)
    freq = models.IntegerField(u'Freq', null=True) 
    user = models.ForeignKey('UserWordFreq', blank=True, null=True)

    def __unicode__(self):
        return self.word

# Create your models here.
class UserFrequency(models.Model):
    freq = models.TextField(u'Freq', null=True)
    user = models.CharField(u'User', max_length=50, null=True)

    def __unicode__(self):
        return self.user

class IpBased(models.Model):
    friend = models.TextField(u'Friend', null=True)
    user = models.CharField(u'User', max_length=50, null=True)

    def __unicode__(self):
        return self.user

class TimeBased(models.Model):
    friend = models.TextField(u'Friend', null=True)
    user = models.CharField(u'User', max_length=50, null=True)

    def __unicode__(self):
        return self.user

class UserInteraction(models.Model):
    fans = models.TextField(u'Fans', null=True)
    user = models.CharField(u'User', max_length=50, null=True)

    def __unicode__(self):
        return self.user

class Post(models.Model):
    title = models.CharField(u'Title', max_length=50, null=True)
    date = models.CharField(u'Date', max_length=50, null=True)
    url = models.CharField(u'Url', max_length=50, null=True)
    author = models.CharField(u'Author', max_length=50, null=True)

    def __unicode__(self):
        return self.title

class Comment(models.Model):
    content = models.CharField(u'Content', max_length=50, null=True)
    score = models.IntegerField(u'Score', null=True)    
    user = models.CharField(u'User', max_length=50, null=True)
    post = models.ForeignKey('Post', blank=True, null=True)
    def __unicode__(self):
        return self.user

class Node(models.Model):
    group = models.IntegerField(u'Group', null=True)    
    name = models.CharField(u'Name', max_length=50, null=True)
    graphs = models.ManyToManyField('Graph')
    def __unicode__(self):
        return self.name

class Link(models.Model):
    source = models.IntegerField(u'Source', null=True)
    target = models.IntegerField(u'Target', null=True)
    total_comment = models.IntegerField(u'Total_comment', null=True)
    fan_comment = models.IntegerField(u'Fan_comment', null=True)
    comment_rate = models.FloatField(u'Comment_rate', null=True)
    width = models.FloatField(u'Width', null=True)
    value = models.IntegerField(u'Value', null=True)
    graphs = models.ManyToManyField('Graph')

class Graph(models.Model):
    user = models.CharField(u'User', max_length=50, null=True)
    def __unicode__(self):
        return self.user