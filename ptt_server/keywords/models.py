from __future__ import unicode_literals

from django.db import models

# Create your models here.


class TokenAmount(models.Model):
    amount = models.IntegerField(u'Amount', null=True)    
    token = models.CharField(u'Token', max_length=50, null=True)
    MostUsedToken = models.ForeignKey('MostUsedToken', blank=True, null=True)
    def __unicode__(self):
        return self.token

class MostUsedToken(models.Model):
    date = models.CharField(u'Date', max_length=50, null=True)
    def __unicode__(self):
        return self.date


class NegTokenScore(models.Model):
    score = models.FloatField(u'Score', null=True)    
    token = models.CharField(u'Token', max_length=50, null=True)
    CommentNegToken = models.ForeignKey('CommentNegToken', blank=True, null=True)
    def __unicode__(self):
        return self.token

class CommentNegToken(models.Model):
    date = models.CharField(u'Date', max_length=50, null=True)
    def __unicode__(self):
        return self.date

class PosTokenScore(models.Model):
    score = models.FloatField(u'Score', null=True)    
    token = models.CharField(u'Token', max_length=50, null=True)
    CommentPosToken = models.ForeignKey('CommentPosToken', blank=True, null=True)
    def __unicode__(self):
        return self.token

class CommentPosToken(models.Model):
    date = models.CharField(u'Date', max_length=50, null=True)
    def __unicode__(self):
        return self.date

class NegLegisScore(models.Model):
    score = models.FloatField(u'Score', null=True)    
    token = models.CharField(u'Token', max_length=50, null=True)
    NegLegisToken = models.ForeignKey('NegLegisToken', blank=True, null=True)
    def __unicode__(self):
        return self.token

class NegLegisToken(models.Model):
    date = models.CharField(u'Date', max_length=50, null=True)
    def __unicode__(self):
        return self.date