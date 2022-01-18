from django.contrib import admin
from .models import *

class AgentAdmin(admin.ModelAdmin):
    list_display = ('agent_id', 'agent_fio', 'organization')
class ClientAdmin(admin.ModelAdmin):
    list_display = ('client_id', 'client_fio', 'date_birthday', 'place_birthday')


class PassportAdmin(admin.ModelAdmin):
    list_display = ('passport_id', 'passport_seria', 'passport_number', 'passport_date_issue', 'passport_date_expiration', 'passport_authority')


class ClientStatusAdmin(admin.ModelAdmin):
    list_display = ('client_status_id', 'client_status_name')

class WorkerAdmin(admin.ModelAdmin):
    list_display = ('worker_id', 'worker_fio', 'organization', 'position', 'date_birthday', 'photo')


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('organization_id', 'organization_name')


class PositionAdmin(admin.ModelAdmin):
    list_display = ('position_id', 'position_name')




admin.site.register(Agent, AgentAdmin)
admin.site.register(Worker, WorkerAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Passport, PassportAdmin)
admin.site.register(InterPassport)
admin.site.register(ClientStatus, ClientStatusAdmin)