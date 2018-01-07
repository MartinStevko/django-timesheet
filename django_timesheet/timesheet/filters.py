
import django_selector as ds

class TaskFilter(ds.FilterSet):

    from_date = ds.DateFilter(name='date', lookup_expr='gte', label='Von')
    to_date = ds.DateFilter(name='date', lookup_expr='lte', label='Bis')