from django.contrib import admin

from electionnight.models import (APElectionMeta, PageContent, PageContentType,
                                  PageType, CandidateColorOrder)

from .ap_election_meta import APElectionMetaAdmin
from .page_content import PageContentAdmin
from .color_order import CandidateColorOrderAdmin

admin.site.register(APElectionMeta, APElectionMetaAdmin)
admin.site.register(PageContent, PageContentAdmin)
admin.site.register(PageContentType)
admin.site.register(PageType)
admin.site.register(CandidateColorOrder, CandidateColorOrderAdmin)
