# from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings


class Account(models.Model):
    account = models.OneToOneField('Worker', models.DO_NOTHING, primary_key=True)
    login = models.CharField(max_length=50)
    password = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'account'


class Agent(models.Model):
    agent_id = models.AutoField(primary_key=True)
    organization = models.ForeignKey('Organization', models.DO_NOTHING)
    agent_fio = models.CharField(max_length=255)
    agent_name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'agent'


class Agreement(models.Model):
    agreement_id = models.AutoField(primary_key=True)
    agreement_number = models.CharField(max_length=50)
    worker = models.ForeignKey('Worker', models.DO_NOTHING)
    date_agreement = models.DateTimeField()
    organization = models.ForeignKey('Organization', models.DO_NOTHING)
    agent = models.ForeignKey(Agent, models.DO_NOTHING, blank=True, null=True)
    client = models.ForeignKey('Client', models.DO_NOTHING)
    numbers_tourist = models.IntegerField()
    date_start = models.DateField()
    date_end = models.DateField()

    class Meta:
        managed = False
        db_table = 'agreement'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150, null=True)
    last_name = models.CharField(max_length=150, null=True)
    email = models.CharField(max_length=254, null=True)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class City(models.Model):
    city_id = models.AutoField(primary_key=True)
    city_name = models.CharField(max_length=50)
    country = models.ForeignKey('Country', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'city'


class CityInAgreement(models.Model):
    city_in_agreement_id = models.AutoField(primary_key=True)
    city = models.ForeignKey(City, models.DO_NOTHING)
    agreement = models.ForeignKey(Agreement, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'city_in_agreement'


class Client(models.Model):
    client_id = models.AutoField(primary_key=True)
    client_name = models.CharField(max_length=50)
    client_fio = models.CharField(max_length=255)
    client_status = models.ForeignKey('ClientStatus', models.DO_NOTHING)
    gender = models.CharField(max_length=1)
    date_birthday = models.DateField()
    place_birthday = models.CharField(max_length=255)
    passport_seria = models.CharField(max_length=2)
    passport_number = models.CharField(max_length=8)
    passport_date_issue = models.DateField()
    passport_date_expiration = models.DateField()
    passport_authority = models.CharField(max_length=255)

    def get_absolute_url(self):
        return f'/client_list'


    class Meta:
        managed = False
        db_table = 'client'


class ClientStatus(models.Model):
    client_status_id = models.AutoField(primary_key=True)
    client_status_name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'client_status'


class Contract(models.Model):
    contract_id = models.AutoField(primary_key=True)
    contract_number = models.CharField(max_length=50)
    worker = models.ForeignKey('Worker', models.DO_NOTHING)
    organization = models.ForeignKey('Organization', models.DO_NOTHING)
    contract_date = models.DateTimeField()
    currency_code = models.ForeignKey('Currency', models.DO_NOTHING, db_column='currency_code')
    amount = models.IntegerField()
    agreement = models.ForeignKey(Agreement, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'contract'


class Country(models.Model):
    country_id = models.AutoField(primary_key=True)
    country_name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'country'


class Currency(models.Model):
    currency_code = models.IntegerField(primary_key=True)
    currency_name = models.CharField(max_length=15)
    course = models.FloatField()

    class Meta:
        managed = False
        db_table = 'currency'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Hotel(models.Model):
    hotel_id = models.AutoField(primary_key=True)
    hotel_name = models.CharField(max_length=50)
    address = models.CharField(max_length=255)
    category = models.IntegerField()
    city = models.ForeignKey(City, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'hotel'


class InterPassport(models.Model):
    inter_passport_id = models.AutoField(primary_key=True)
    inter_passport_seria = models.CharField(max_length=2)
    inter_passport_number = models.CharField(max_length=7)
    inter_passport_date_issue = models.DateField()
    inter_passport_date_expiration = models.DateField()
    inter_passport_authority = models.CharField(max_length=255)
    citizenship = models.CharField(max_length=50)
    state_code = models.CharField(max_length=3)

    class Meta:
        managed = False
        db_table = 'inter_passport'


class Organization(models.Model):
    organization_id = models.AutoField(primary_key=True)
    organization_name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'organization'


class Passport(models.Model):
    passport_id = models.AutoField(primary_key=True)
    passport_seria = models.CharField(max_length=2)
    passport_number = models.CharField(max_length=8)
    passport_date_issue = models.DateField()
    passport_date_expiration = models.DateField()
    passport_authority = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'passport'


class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    worker = models.ForeignKey('Worker', models.DO_NOTHING)
    payment_number = models.CharField(max_length=50)
    payment_date = models.DateTimeField()
    contract = models.ForeignKey(Contract, models.DO_NOTHING)
    amount = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'payment'


class Position(models.Model):
    position_id = models.AutoField(primary_key=True)
    position_name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'position'


class RoomType(models.Model):
    room_type_id = models.AutoField(primary_key=True)
    room_type_name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'room_type'


class Route(models.Model):
    route_id = models.AutoField(primary_key=True)
    hotel = models.ForeignKey(Hotel, models.DO_NOTHING)
    check_in_date = models.DateTimeField()
    room_type = models.ForeignKey(RoomType, models.DO_NOTHING)
    departure_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'route'


class RouteInContract(models.Model):
    route_in_contract_id = models.AutoField(primary_key=True)
    route = models.ForeignKey(Route, models.DO_NOTHING)
    contract = models.ForeignKey(Contract, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'route_in_contract'


class Tour(models.Model):
    tour_id = models.AutoField(primary_key=True)
    payment = models.ForeignKey(Payment, models.DO_NOTHING)
    voucher = models.ForeignKey('Voucher', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'tour'


class TouristInContract(models.Model):
    tourist_in_contract_id = models.AutoField(primary_key=True)
    tourist = models.ForeignKey(Client, models.DO_NOTHING)
    contract = models.ForeignKey(Contract, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'tourist_in_contract'


class Transport(models.Model):
    transport_id = models.AutoField(primary_key=True)
    transport_name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'transport'


class Voucher(models.Model):
    voucher_id = models.AutoField(primary_key=True)
    client = models.ForeignKey(Client, models.DO_NOTHING)
    transport = models.ForeignKey(Transport, models.DO_NOTHING)
    transfer = models.CharField(max_length=4)
    food = models.CharField(max_length=11)

    class Meta:
        managed = False
        db_table = 'voucher'


class Worker(models.Model):
    worker_id = models.AutoField(primary_key=True)
    organization = models.ForeignKey(Organization, models.DO_NOTHING)
    position = models.ForeignKey(Position, models.DO_NOTHING)
    worker_name = models.CharField(max_length=50)
    worker_fio = models.CharField(max_length=255)
    date_birthday = models.DateField()
    photo = models.ImageField(blank=True, null=True)
    user = models.OneToOneField(AuthUser, models.CASCADE, db_column='user', blank=True, null=True)


    class Meta:
        managed = False
        db_table = 'worker'
