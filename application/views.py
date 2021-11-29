from django.shortcuts import render, redirect
from django import views
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login
from .models import *
from .forms import *
from django.views.generic import UpdateView
import datetime
from django.contrib.auth.hashers import make_password
from django.core.files.storage import FileSystemStorage


class ClientListView(views.View):

    def get(self, request, *args, **kwargs):
        search = request.GET.get("q")
        if search == None:
            clients = Client.objects.filter()
        else:
            clients = Client.objects.filter(client_fio__icontains=request.GET.get("q"))

        context = {
            'clients': clients,
        }
        return render(request, 'clients/client_list.html', context)


class WorkerListView(views.View):

    def get(self, request, *args, **kwargs):
        search = request.GET.get("q")
        if search == None:
            workers = Worker.objects.filter()
            agents = Agent.objects.filter()
        else:
            workers = Worker.objects.filter(worker_fio__icontains=request.GET.get("q"))
            agents = Agent.objects.filter(agent_fio__icontains=request.GET.get("q"))

        context = {
            'workers': workers,
            'agents': agents,
        }
        return render(request, 'workers/worker_list.html', context)


class AgentListView(views.View):

    def get(self, request, *args, **kwargs):
        search = request.GET.get("q")
        if search == None:
            agents = Agent.objects.filter()
        else:
            agents = Agent.objects.filter(agent_fio__icontains=request.GET.get("q"))

        context = {
            'agents': agents,
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


def add_client(request):
    error = ''
    if request.method == 'POST':
        form = ClientCreateForm(request.POST)
        if form.is_valid():
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
    if request.method == 'POST':
        check_unique = Agent.objects.filter(agent_fio=request.POST['agent_fio'],  organization_id=request.POST['organization_id']).exists()
        if not check_unique:
            form = AgentCreateForm(request.POST)
            if form.is_valid():
                form.save()
                worker = Worker.objects.get(user=request.user.id)
                position = Position.objects.get(position_id=worker.position_id)
                if position.position_id == 1:
                    return redirect('agents/agent_list')
                else:
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
        'error': error
    }

    return render(request, 'agents/add_agent.html', context)


class WorkerCardView(UpdateView):

    model = Worker
    fields = ['worker_name', 'worker_fio', 'date_birthday', 'photo']
    template_name = 'workers/worker_card.html'


class AgentCardView(UpdateView):

    model = Agent
    fields = ['agent_name', 'agent_fio']
    template_name = 'agents/agent_card.html'


def add_worker(request):
    error= ''
    if request.method == 'POST':
        check_unique = Worker.objects.filter(worker_fio=request.POST['worker_fio'], date_birthday=request.POST['date_birthday'], position=request.POST['position']).exists()
        if not check_unique:
            last_id = AuthUser.objects.latest('id').id
            generate_username = request.POST['worker_name']
            form_user = UserCreateForm(
                {'password': make_password('django123'),
                 'last_login': str(datetime.datetime.now()), 'username': generate_username,
                 'date_joined': str(datetime.datetime.now()), 'is_staff': 1, 'is_active': 1,
                 'is_superuser': 0})
            form = WorkerCreateForm(request.POST, request.FILES)

            if form_user.is_valid() and form.is_valid():
                user_instance = form_user.save(commit=False)
                form_user.save()
                a = form.save(commit=False)
                a.user = user_instance
                a.save()
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
        'error': error
    }

    return render(request, 'workers/add_worker.html', context)