from crudlfap import crudlfap


class HistoryView(crudlfap.ObjectView, crudlfap.ListView):
    menus = ['object']
    material_icon = 'history'

    def get_filterset_kwargs(self):
        return {
            'data': self.request.GET or None,
            'request': self.request,
            'queryset': self.get_queryset(),
        }
