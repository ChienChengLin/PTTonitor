from django.contrib import admin

from keywords.models import TokenAmount
from keywords.models import MostUsedToken
from keywords.models import NegTokenScore
from keywords.models import CommentNegToken
from keywords.models import PosTokenScore
from keywords.models import CommentPosToken
from keywords.models import NegLegisScore
from keywords.models import NegLegisToken
# Register your models here.


admin.site.register(TokenAmount)
admin.site.register(MostUsedToken)
admin.site.register(NegTokenScore)
admin.site.register(CommentNegToken)
admin.site.register(PosTokenScore)
admin.site.register(CommentPosToken)
admin.site.register(NegLegisScore)
admin.site.register(NegLegisToken)