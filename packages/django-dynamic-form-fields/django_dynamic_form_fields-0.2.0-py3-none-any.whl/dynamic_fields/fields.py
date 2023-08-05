# -*- coding: utf-8 -*-
import inspect
from typing import Callable, List, Type

from django.core import signing
from django.db.models import Model
from django.forms import Select


class DynamicChoicesWidget(Select):
    template_name = 'dynamic_fields/forms/widgets/dynamic_select.html'

    class Media:
        js = [
            'dynamic_fields/js/dynamic_fields.js',
        ]

    def __init__(self,
                 # required
                 model: Type[Model],
                 callback: Callable[..., List],
                 depends_field: str,
                 # optional
                 no_value_disable: bool=True,
                 include_empty_choice: bool=False,
                 empty_choice_label: str='---------',
                 # defaults to super()
                 attrs=None, choices=()):
        self.depends_field = depends_field
        self.model = model
        self.no_value_disable = no_value_disable
        self.include_empty_choice = include_empty_choice
        self.empty_choice_label = empty_choice_label

        try:
            self.callback = '{}.{}'.format(inspect.getmodule(callback).__name__, callback.__name__)
        except AttributeError:
            raise Exception("callback cannot be a lambda")

        super().__init__(attrs, choices)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context.update({
            'df': {
                'depends': self.depends_field,
                'model': signing.dumps('{}.{}'.format(self.model._meta.app_label, self.model._meta.model_name)),
                'no_value_disable': self.no_value_disable,
                'include_empty_choice': self.include_empty_choice,
                'empty_choice_label': self.empty_choice_label,
                'callback': signing.dumps(self.callback),
            },
        })
        return context
