from datetime import timedelta

from django.utils import timezone
from django.utils.dateparse import parse_date


def resolver_periodo(request):
    hoje = timezone.localdate()
    period = request.GET.get("period", "30")

    if period == "custom":
        start = parse_date(request.GET.get("start", "")) or (hoje - timedelta(days=30))
        end = parse_date(request.GET.get("end", "")) or hoje
        return start, end

    try:
        dias = int(period)
    except ValueError:
        dias = 30

    return hoje - timedelta(days=dias), hoje