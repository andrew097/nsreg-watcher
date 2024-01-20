from django.shortcuts import render
from django.http import HttpResponseNotFound
from django.db.models import Q, Min

from .models import Price
from .forms import CompaniesSortForm


SORT_FIELD_NAMES = {
    'CN': 'registrator__name',
    'CI': 'registrator__city',
    'RE': 'price_reg',
    'PR': 'price_prolong',
    'PE': 'price_change',

}


def registrator_list(request):
    if request.method == "POST":
        form = CompaniesSortForm(request.POST)
        if form.is_valid():
            sort_by = (form.cleaned_data['reverse_order']
                       + SORT_FIELD_NAMES.get(
                        form.cleaned_data['sort_by'], 'name'))
            search = form.cleaned_data['search']
            print(f"****************** SORT BY: {sort_by}")

    else:
        form = CompaniesSortForm()
        sort_by = 'id'
        search = ''

    if search:
        companies = Price.objects.filter(Q(registrator__name__icontains=search) | Q(
            registrator__city__icontains=search) | Q(price_reg__icontains=search))
        print("****************** SEARCH")
    else:
        companies = Price.objects.filter()

    # companies = companies.order_by('registrator_id', '-parse__id')
    # companies = Price.objects.filter(id__in=companies).distinct('registrator_id')
    # companies = Price.objects.filter(id__in=companies).order_by(sort_by)
    companies = companies.annotate(
        min_status=Min('reg_status', 'prolong_status', 'change_status')
    )

    companies = companies.order_by('min_status', 'registrator_id', '-parse__id', sort_by)

    return render(request, 'registrator-list.html', {'companies': companies, 'form': form})


def registrator_details(request, id):
    try:
        company = Price.objects.get(id=id)
    except Price.DoesNotExist:
        return HttpResponseNotFound(f"Компания с идентификатором {id} в базе не найдена.")
    return render(request, 'registrator-details.html', {'company': company})


def about(request):
    return render(request, 'about-us.html', )


def project_view(request):
    return render(request, 'project.html')
