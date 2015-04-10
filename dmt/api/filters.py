from rest_framework import filters


class ProjectSearchFilter(filters.SearchFilter):
    def get_search_terms(self, request):
        """
        Search terms are set by a ?search=... query parameter,
        and may be comma delimited.

        Unlike DRF's upstream search tokenizer, this one allows to
        search for tokens that contain spaces.
        """
        params = request.query_params.get(self.search_param, '')
        params = params.replace(',', ' ')
        return [params] + params.split()

    @staticmethod
    def startswith_term(name, term):
        """Sort by whether or not name starts with term"""
        if name.lower().startswith(term.lower()):
            return -1
        else:
            return 1

    def filter_queryset(self, request, queryset, view):
        queryset = super(ProjectSearchFilter, self).filter_queryset(
            request, queryset, view)

        term = request.query_params.get(self.search_param, '')
        if term:
            # Put startswith matches at the beginning, and then sort
            # alphabetically by name.
            queryset = sorted(
                queryset,
                key=lambda p: (self.startswith_term(p.name, term), p.name))

        return queryset
