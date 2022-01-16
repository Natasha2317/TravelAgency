from hashlib import pbkdf2_hmac
from django.shortcuts import render, redirect
from django import views
from django.http import HttpResponseRedirect, request
from django.contrib.auth import authenticate, login
from .models import *
from .forms import *
from django.views.generic import UpdateView, DeleteView
import datetime
from django.contrib.auth.hashers import make_password
from django.core.files.storage import FileSystemStorage
from django.db import transaction
from django.contrib import messages
from requests import get
from bs4 import BeautifulSoup as bs


def currency_list(request):

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Host":"www.cbr.ru:443",
        "Accept-Encoding": "gzip, deflate, sdch, br",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36"
    }

    body = get('http://www.cbr.ru/currency_base/daily/', headers=headers)
    for_bs = body.text
    soup = bs(for_bs, 'html.parser')

    currency_list = Currency.objects.all()
    currency = soup.find_all('td')

    if request.method == 'POST':
        i = 4
        for item in currency_list:
            Currency.objects.filter(currency_code=item.currency_code).update(course=currency[i].text.replace(',', '.'))
            i += 5

    context = {
        'currency_list': currency_list

    }
    return render(request, 'documents/currency_list.html', context)


class ClientListView(views.View):

    def get(self, request, *args, **kwargs):
        search = request.GET.get("q")
        if search == None:
            clients = Client.objects.filter()
            search = ''
        else:
            clients = Client.objects.filter(client_fio__icontains=request.GET.get("q"))

        context = {
            'clients': clients,
            'search': search,
        }
        return render(request, 'clients/client_list.html', context)


class WorkerListView(views.View):

    def get(self, request, *args, **kwargs):
        search = request.GET.get("q")
        if search == None:
            workers = Worker.objects.filter()
            agents = Agent.objects.filter()
            search = ''
        else:
            workers = Worker.objects.filter(worker_fio__icontains=request.GET.get("q"))
            agents = Agent.objects.filter(agent_fio__icontains=request.GET.get("q"))

        context = {
            'workers': workers,
            'agents': agents,
            'search': search,
        }
        return render(request, 'workers/worker_list.html', context)


class AgentListView(views.View):

    def get(self, request, *args, **kwargs):
        search = request.GET.get("q")
        if search == None:
            agents = Agent.objects.filter()
            search = ''
        else:
            agents = Agent.objects.filter(agent_fio__icontains=request.GET.get("q"))

        context = {
            'agents': agents,
            'search': search,
        }
        return render(request, 'agents/agent_list.html', context)


class LoginView(views.View):

    def get(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        context = {'form': form}
        return render(request, 'authorization.html', context)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect('account')
        context = {'form': form}
        return render(request, 'authorization.html', context)


class AccountView(views.View):

    def get(self, request, *args, **kwargs):

        worker = Worker.objects.get(user=request.user.id)
        position = Position.objects.get(position_id=worker.position_id)
        # organizationW = organization.organization_name

        context = {
            'worker': worker,
        }

        if (position.position_id == 1):
            return render(request, 'meneger_lk.html', context)
        if (position.position_id == 2):
            return render(request, 'accountant_lk.html', context)
        if (position.position_id == 3):
            return render(request, 'admin_lk.html', context)


class ClientCardView(UpdateView):

    model = Client
    fields = ['client_name', 'client_fio', 'gender', 'date_birthday', 'place_birthday', 'passport_seria', 'passport_number', 'client_status', 'passport_date_issue', 'passport_date_expiration', 'passport_authority']
    template_name = 'clients/client_card.html'


def delete_image(request, pk):
    person = Worker.objects.get(worker_id=pk)
    image = person.photo
    image_del = image.delete()
    messages.add_message(request, messages.INFO, 'Сотрудник успешно изменён!')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



def add_client(request):
    error = ''
    if request.method == 'POST':
        form = ClientCreateForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                form.save()
            return redirect('clients/client_list')
        else:
            error = 'Форма заполнена некорректно'

    clientStatus = ClientStatus.objects.all()
    form = ClientCreateForm()

    context = {
        'form': form,
        'clientStatus': clientStatus,
    }

    return render(request, 'clients/add_client.html', context)


def add_agent(request):
    error= ''
    double = ''
    if request.method == 'POST':
        check_unique = Agent.objects.filter(agent_name=request.POST['agent_name'], agent_fio=request.POST['agent_fio'], organization=request.POST['organization']).exists()

        if check_unique:
            double = Agent.objects.filter(agent_name=request.POST['agent_name'], agent_fio=request.POST['agent_fio'], organization=request.POST['organization']).latest('agent_id')

        if not check_unique or 'double' in request.POST:
            req = request.POST.copy()
            if 'double' in request.POST:
                req.pop('double')
            form = AgentCreateForm(req)
            if form.is_valid():
                form.save()
                return redirect('workers/worker_list')
            else:
                error = 'Форма заполнена некорректно'
        else:
            error = 'Агент с такими же данными уже существует'

    organizations = Organization.objects.all()
    form = AgentCreateForm()

    context = {
        'form': form,
        'organizations': organizations,
        'error': error,
        'init': double,
    }

    return render(request, 'agents/add_agent.html', context)



def worker_card(request, pk):
    error = ''
    person = Worker.objects.get(worker_id=pk)
    if request.method == 'POST':
        form = WorkerCreateForm(request.POST, request.FILES, instance=person)
        if form.is_valid():
            with transaction.atomic():
                worker_instance = form.save(commit=False)
                worker_instance.save()
                messages.add_message(request, messages.INFO, 'Сотрудник успешно изменён')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        else:
            error = 'Форма заполнена некорректно'

    positions = Position.objects.all()
    organizations = Organization.objects.all()
    return render(request, 'workers/worker_card.html', {'worker': person, 'positions': positions,
                                                             'organizations': organizations,
                                                             'error': error,})



def agent_card(request, pk):
    error = ''
    person = Agent.objects.get(agent_id=pk)
    if request.method == 'POST':
        form = AgentCreateForm(request.POST, instance=person)
        if form.is_valid():
            agent_instance = form.save(commit=False)
            agent_instance.save()
            messages.add_message(request, messages.INFO, 'Сотрудник успешно изменён')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            error = 'Форма заполнена некорректно'

    organizations = Organization.objects.all()
    return render(request, 'agents/agent_card.html', {'agent': person, 'organizations': organizations,
                                                             'error': error})


def add_worker(request):
    error= ''
    double = ''
    if request.method == 'POST':
        check_unique = Worker.objects.filter(worker_name=request.POST['worker_name'], worker_fio=request.POST['worker_fio'], date_birthday=request.POST['date_birthday'], position=request.POST['position']).exists()

        if check_unique:
                double = Worker.objects.filter(worker_name=request.POST['worker_name'], worker_fio=request.POST['worker_fio'], date_birthday=request.POST['date_birthday'], position=request.POST['position']).latest('worker_id')

        if not check_unique or 'double' in request.POST:
            req = request.POST.copy()
            if 'double' in request.POST:
                req.pop('double')
            last_id = AuthUser.objects.latest('id').id
            generate_username = ((request.POST['worker_fio']).split())[0]
            form_user = UserCreateForm(
                {'password': make_password('django123'),
                 'last_login': str(datetime.datetime.now()), 'username': generate_username,
                 'date_joined': str(datetime.datetime.now()), 'is_staff': 1, 'is_active': 1,
                 'is_superuser': 0})
            form = WorkerCreateForm(req)
            if form_user.is_valid() and form.is_valid():
                with transaction.atomic():
                    user_instance = form_user.save(commit=False)
                    form_user.save()
                    worker_instance = form.save(commit=False)
                    worker_instance.user = user_instance
                    worker_instance.save()
                    return redirect('workers/worker_list')
            else:
                error = str(form_user.errors) + str(form.errors)
        else:
            error = 'Сотрудник с такими же данными уже существует'

    positions = Position.objects.all()
    organizations = Organization.objects.all()
    form = WorkerCreateForm()

    context = {
        'form': form,
        'positions': positions,
        'organizations': organizations,
        'error': error,
        'init': double
    }

    return render(request, 'workers/add_worker.html', context)


class AgreementListView(views.View):

    def get(self, request, *args, **kwargs):

        agreements = Agreement.objects.filter()

        context = {
            'agreements': agreements,
        }
        return render(request, 'documents/agreement_list.html', context)


class ContractListView(views.View):

    def get(self, request, *args, **kwargs):

        contracts = Contract.objects.filter()

        context = {
            'contracts': contracts,
        }
        return render(request, 'documents/contract_list.html', context)

class PaymentListView(views.View):

    def get(self, request, *args, **kwargs):

        payments = Payment.objects.filter()

        context = {
            'payments': payments,
        }
        return render(request, 'documents/payment_list.html', context)


def add_agreement(request):
    error= ''
    if request.method == 'POST':
        city = request.POST.get('city')
        form_city_agreement = CityAgreementCreateForm(request.POST)
        form = AgreementCreateForm(request.POST)
        worker = Worker.objects.get(user=request.user.id)
        if form.is_valid():
            agreement_instance = form.save(commit=False)
            agreement_instance.worker_id = worker.worker_id
            agreement_instance.save()
            last_agreement_id = Agreement.objects.all().last().agreement_id
            form_city_agreement = CityAgreementCreateForm(
            {'city': city, 'agreement': last_agreement_id})
            form_city_agreement.save()
            return redirect('agreement_card/'+ str(last_agreement_id))
        else:
            error = str(form_city_agreement.errors) + str(form.errors)


    positions = Position.objects.all()
    organizations = Organization.objects.all()
    countries = Country.objects.all()
    cities = City.objects.all()
    clients = Client.objects.all()
    agents = Agent.objects.all()
    form = AgreementCreateForm()

    context = {
        'form': form,
        'positions': positions,
        'organizations': organizations,
        'error': error,
        'countries': countries,
        'cities': cities,
        'clients': clients,
        'agents': agents,
    }

    return render(request, 'documents/add_agreement.html', context)


def add_contract(request):
    error= ''
    agreement = Agreement.objects.all().last()
    if request.method == 'POST':
        form_route = RouteCreateForm(request.POST)
        form_tourist = TouristInContractForm(request.POST)
        form_route_in_contract = RouteInContractCreateForm(request.POST)
        form = ContractCreateForm(request.POST)
        worker = Worker.objects.get(user=request.user.id)
        tourist = request.POST.get('tourist')
        if form.is_valid():
            contract_instance = form.save(commit=False)
            contract_instance.worker_id = worker.worker_id
            contract_instance.agreement_id = agreement.agreement_id
            contract_instance.save()
            last_contract_id = Contract.objects.all().last().contract_id
            form_tourist = TouristInContractForm(
                {'tourist': tourist, 'contract': last_contract_id})
            form_tourist.save()
            route_instance = form_route.save(commit=False)
            route_instance.save()
            last_route_id = Route.objects.all().last().route_id
            form_route_in_contract = RouteInContractCreateForm(
                {'route': last_route_id, 'contract': last_contract_id})
            form_route_in_contract.save()
            return redirect('contract_card/'+ str(last_contract_id))
        else:
            error = str(form.errors)

    positions = Position.objects.all()
    organizations = Organization.objects.all()
    clients = Client.objects.all()
    get_client = agreement.client_id
    agents = Agent.objects.all()
    form = ContractCreateForm()
    cities = City.objects.all()
    hotels = Hotel.objects.all()
    countries = Country.objects.all()
    currency = Currency.objects.all()
    agent_use = Agent.objects.filter(agent_id=agreement.agent_id)
    routes = Route.objects.all()
    room_types = RoomType.objects.all()
    city_in_agreement = CityInAgreement.objects.filter(agreement_id=agreement.agreement_id)



    def get_array():
        array = []
        item = 0
        while item <= len(city_in_agreement)-1:
            if city_in_agreement[item]:
                get_city_in_contract = city_in_agreement[item]
                city_in_route = get_city_in_contract.city_id
                array.append(city_in_route)
                item += 1
            else:
                break
        return array


    context = {
        'form': form,
        'positions': positions,
        'organizations': organizations,
        'error': error,
        'countries': countries,
        'cities': cities,
        'clients': clients,
        'agents': agents,
        'agreement': agreement,
        'hotels': hotels,
        'routes': routes,
        'get_client': get_client,
        'agent_use': agent_use,
        'array': get_array(),
        'currency': currency,
        'room_types': room_types,
        }

    return render(request, 'documents/add_contract.html', context)


def add_payment(request):
    error= ''
    if request.method == 'POST':
        form = PaymentCreateForm(request.POST)
        worker = Worker.objects.get(user=request.user.id)
        if form.is_valid():
            payment_instance = form.save(commit=False)
            payment_instance.worker_id = worker.worker_id
            last_contract_id = Contract.objects.all().last().contract_id
            payment_instance.contract_id = last_contract_id
            payment_instance.save()
            return redirect('documents/payment_list')
        else:
            error = str(form.errors)

    contract = Contract.objects.all().last()
    contracts = Contract.objects.all()
    # get_currency_amount = Contract.objects.all().last().amount
    # currency = Currency.objects.all()
    get_currency = contract.currency_code
    currency_card = get_currency.currency_code
    get_currency_amount = contract.amount
    currency_card = Currency.objects.get(currency_code=currency_card)
    get_currency_course = currency_card.course
    payment_amount = int(get_currency_amount)*int(get_currency_course)
    positions = Position.objects.all()
    organizations = Organization.objects.all()
    countries = Country.objects.all()
    cities = City.objects.all()
    clients = Client.objects.all()
    agents = Agent.objects.all()
    form = AgreementCreateForm()

    context = {
        'form': form,
        'positions': positions,
        'organizations': organizations,
        'error': error,
        'countries': countries,
        'cities': cities,
        'clients': clients,
        'agents': agents,
        'payment_amount': payment_amount,
        'contract': contract,
        'contracts': contracts
    }

    return render(request, 'documents/add_payment.html', context)


def agreement_card(request, pk):
    error = ''

    agreement = Agreement.objects.get(agreement_id=pk)
    if request.method == 'POST':
        form = AgreementCreateForm(request.POST, instance=agreement)
        if form.is_valid():
                # city_in_agreement = CityInAgreement.objects.get(city_in_agreement=agreement.city_in_agreement)
                # city_ag = City.objects.get(city_id=city_in_agreement.city)
                # country_ag = Country.objects.get(country_id=city_ag.country)
                agreement_instance = form.save(commit=False)
                agreement_instance.save()
                messages.add_message(request, messages.INFO, 'Соглашение успешно изменено')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        else:
            error = 'Форма заполнена некорректно'

    agreement = Agreement.objects.get(agreement_id=pk)
    positions = Position.objects.all()
    organizations = Organization.objects.all()
    clients = Client.objects.all()
    agents = Agent.objects.all()
    form = AgreementCreateForm()
    cities = City.objects.all()
    countries = Country.objects.all()
    # contract = Contract.objects.get(agreement_id=pk)
    currency = Currency.objects.all()
    # get_currency = contract.currency_code
    # currency_card = get_currency.currency_code
    city_in_agreement = CityInAgreement.objects.filter(agreement=agreement.agreement_id)
    # city_ag = city_in_agreement.city_id
    # country_ag = Country.objects.get(country_id=city_ag.country)
    def get_array():
            array = []
            item = 0
            while item <= len(city_in_agreement)-1:
                if city_in_agreement[item]:
                    get_city_in_agreement = city_in_agreement[item]
                    city_ag = get_city_in_agreement.city_id
                    array.append(city_ag)
                    item += 1
                else:
                    break
            return array

    context = {
        'form': form,
        'positions': positions,
        'organizations': organizations,
        'error': error,
        'countries': countries,
        'cities': cities,
        'clients': clients,
        'agents': agents,
        'agreement': agreement,
        # 'currency_card': currency_card,
        'currency': currency,
        'array': get_array(),
    }
    return render(request, 'documents/agreement_card.html', context)


def contract_card(request, pk):
    error = ''

    contract = Contract.objects.get(contract_id=pk)
    if request.method == 'POST':
        form = ContractCreateForm(request.POST, instance=contract)
        if form.is_valid():
                # city_in_agreement = CityInAgreement.objects.get(city_in_agreement=agreement.city_in_agreement)
                # city_ag = City.objects.get(city_id=city_in_agreement.city)
                # country_ag = Country.objects.get(country_id=city_ag.country)
                contract_instance = form.save(commit=False)
                contract_instance.save()
                messages.add_message(request, messages.INFO, 'Соглашение успешно изменено')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        else:
            error = 'Форма заполнена некорректно'

    agreement = Agreement.objects.get(agreement_id=contract.agreement_id)
    positions = Position.objects.all()
    organizations = Organization.objects.all()
    clients = Client.objects.all()
    get_client = agreement.client_id
    agents = Agent.objects.all()
    form = ContractCreateForm()
    cities = City.objects.all()
    hotels = Hotel.objects.all()
    countries = Country.objects.all()
    currency = Currency.objects.all()
    agent_use = Agent.objects.filter(agent_id=agreement.agent_id)
    get_currency = contract.currency_code
    currency_card = get_currency.currency_code
    get_currency_amount = contract.amount
    routes = Route.objects.all()
    room_types = RoomType.objects.all()
    route_in_contract = RouteInContract.objects.filter(contract_id=contract.contract_id)
    tourist_in_contract = TouristInContract.objects.filter(contract_id=contract.contract_id)

    def get_array():
        array = []
        item = 0
        while item <= len(tourist_in_contract)-1:
            if tourist_in_contract[item]:
                get_tourist_in_contract = tourist_in_contract[item]
                client_tourist = get_tourist_in_contract.tourist_id
                array.append(client_tourist)
                item += 1
            else:
                break
        return array

    def get_array_routes():
            array_routes = []
            item = 0
            while item <= len(route_in_contract)-1:
                if route_in_contract[item]:
                    get_route_in_contract = route_in_contract[item]
                    route_contract = get_route_in_contract.route_id
                    array_routes.append(route_contract)
                    item += 1
                else:
                    break
            return array_routes


    context = {
        'form': form,
        'positions': positions,
        'organizations': organizations,
        'error': error,
        'countries': countries,
        'cities': cities,
        'clients': clients,
        'agents': agents,
        'agreement': agreement,
        'hotels': hotels,
        'routes': routes,
        'get_client': get_client,
        'tourist_in_contract': tourist_in_contract,
        'agent_use': agent_use,
        'contract': contract,
        'array': get_array(),
        'array_routes': get_array_routes(),
        'currency_card': currency_card,
        'currency': currency,
        'get_currency_amount': get_currency_amount,
        'room_types': room_types,
        }
    return render(request, 'documents/contract_card.html', context)