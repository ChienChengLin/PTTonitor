from django.contrib import admin
from id_query.models import UserWordFreq
from id_query.models import WordFreq
from id_query.models import UserFrequency
from id_query.models import IpBased
from id_query.models import TimeBased
from id_query.models import UserInteraction
from id_query.models import Post
from id_query.models import Comment
from id_query.models import Node
from id_query.models import Link
from id_query.models import Graph



admin.site.register(UserWordFreq)
admin.site.register(WordFreq)
admin.site.register(UserFrequency)
admin.site.register(IpBased)
admin.site.register(TimeBased)
admin.site.register(UserInteraction)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Node)
admin.site.register(Link)
admin.site.register(Graph)
# Register your models here.
