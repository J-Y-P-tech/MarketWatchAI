from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from core.models import Stock
import decimal


def home(request):
    return render(request, 'pages/home.html')


@login_required(login_url='/accounts/login')
def dashboard(request):
    """
    View that handles dashboard page
    """
    if request.method == 'POST':
        fa_score = request.POST.get('fa_score')
        rsi = request.POST.get('rsi')
        avg_gain_loss = request.POST.get('avg_gain_loss')
        five_year_avg_dividend_yield = request.POST.get('five_year_avg_dividend_yield')
        sort_field = request.POST.get('sort')  # Get the sort field from the clicked button

        all_stocks = Stock.objects.all()

        # Filter
        # fa_score greater than
        if fa_score:
            all_stocks = all_stocks.filter(fa_score__gt=int(fa_score))
        # rsi less than
        if rsi:
            all_stocks = all_stocks.filter(rsi__lte=int(rsi))
        # avg_gain_loss greater than
        if avg_gain_loss:
            all_stocks = all_stocks.filter(avg_gain_loss__gt=decimal.Decimal(avg_gain_loss))
        # five_year_dividend_yield greater than
        if five_year_avg_dividend_yield:
            all_stocks = all_stocks.filter(
                five_year_avg_dividend_yield__gt=decimal.Decimal(five_year_avg_dividend_yield))

        # Retrieve the current sort direction from session or set it to ascending by default
        sort_direction = request.session.get('sort_direction', 'ascending')

        # Sort
        if sort_field:
            if sort_field == request.session.get('sort_field'):
                # If the same field is clicked again, reverse the sort direction
                sort_direction = 'ascending' if sort_direction == 'descending' else 'descending'
            else:
                # If a different field is clicked, set the sort direction to ascending
                sort_direction = 'ascending'

            request.session['sort_direction'] = sort_direction
            request.session['sort_field'] = sort_field

            # Determine the prefix '-' for descending order
            sort_prefix = '-' if sort_direction == 'descending' else ''

            # Sort the queryset based on the selected field and direction
            sort_field_with_prefix = f'{sort_prefix}{sort_field}'
            all_stocks = all_stocks.order_by(sort_field_with_prefix)

        # Set default values if none are provided
        data = {
            'fa_score': fa_score,
            'rsi': rsi,
            'avg_gain_loss': avg_gain_loss,
            'five_year_avg_dividend_yield': five_year_avg_dividend_yield,
            'all_stocks': all_stocks,
        }

        return render(request, 'pages/dashboard.html', data)

    if request.method == 'GET':
        fa_score = request.GET.get('fa_score')
        rsi = request.GET.get('rsi')
        avg_gain_loss = request.GET.get('avg_gain_loss')
        five_year_avg_dividend_yield = request.GET.get('five_year_avg_dividend_yield')

        if not fa_score:
            fa_score = 30
        if not rsi:
            rsi = 40
        if not avg_gain_loss:
            avg_gain_loss = 10
        if not five_year_avg_dividend_yield:
            five_year_avg_dividend_yield = 1

        all_stocks = Stock.objects.all()

        # Filter
        # fa_score greater than
        if fa_score:
            all_stocks = all_stocks.filter(fa_score__gt=int(fa_score))
        # rsi less than
        if rsi:
            all_stocks = all_stocks.filter(rsi__lte=int(rsi))
        # avg_gain_loss greater than
        if avg_gain_loss:
            all_stocks = all_stocks.filter(avg_gain_loss__gt=decimal.Decimal(avg_gain_loss))
        # five_year_dividend_yield greater than
        if five_year_avg_dividend_yield:
            all_stocks = all_stocks.filter(
                five_year_avg_dividend_yield__gt=decimal.Decimal(five_year_avg_dividend_yield))

            # Set default values if none are provided
        data = {
            'fa_score': fa_score,
            'rsi': rsi,
            'avg_gain_loss': avg_gain_loss,
            'five_year_avg_dividend_yield': five_year_avg_dividend_yield,
            'all_stocks': all_stocks,
        }

        return render(request, 'pages/dashboard.html', data)


@login_required(login_url='/accounts/login')
def detail(request, id):
    """
    View for stock detail. By given stock id, checks if
    it is present in model Stock and returns its data to the
    template.
    """
    stock = get_object_or_404(Stock, pk=id)
    data = {
        'stock': stock,
    }

    return render(request, 'pages/detail.html', data)
