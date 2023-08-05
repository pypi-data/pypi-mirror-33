# -*- coding: utf-8 -*-
import importlib
from django.apps import apps
from django.http import JsonResponse, HttpResponseBadRequest
from django.views import View


class DynamicFieldChoicesView(View):
    def post(self, *args, **kwargs):
        parts = self.request.POST.get('call').split('.')

        try:
            mod = importlib.import_module('.'.join(parts[:-1]))
        except ImportError:
            return HttpResponseBadRequest("Invalid callback")

        try:
            func = getattr(mod, parts[-1])
        except AttributeError:
            return HttpResponseBadRequest("Invalid callback")

        model = self.request.POST.get('model')
        choices = func(
            model=apps.get_model(
                app_label=model.split('.')[0],
                model_name=model.split('.')[1],
            ),
            value=self.request.POST.get('value'),
        )
        return JsonResponse(choices, safe=False)
