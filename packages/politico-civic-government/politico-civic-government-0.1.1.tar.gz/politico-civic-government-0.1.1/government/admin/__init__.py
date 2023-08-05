from django.contrib import admin

from government.models import Body, Jurisdiction, Office, Party
from .body import BodyAdmin
from .jurisdiction import JurisdictionAdmin
from .office import OfficeAdmin
from .party import PartyAdmin


admin.site.register(Body, BodyAdmin)
admin.site.register(Jurisdiction, JurisdictionAdmin)
admin.site.register(Office, OfficeAdmin)
admin.site.register(Party, PartyAdmin)
