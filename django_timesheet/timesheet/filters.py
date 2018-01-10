
import django_selector as ds

class TaskFilter(ds.FilterSet):

    reference = ds.CharFilter(name='file__reference', label='Aktenzeichen')
    description = ds.CharFilter(label='Beschreibung')
    from_date = ds.DateFilter(name='date', lookup_expr='gte', label='Von')
    to_date = ds.DateFilter(name='date', lookup_expr='lte', label='Bis')

class FileFilter(ds.FilterSet):

    reference = ds.CharFilter(label='Aktenzeichen')