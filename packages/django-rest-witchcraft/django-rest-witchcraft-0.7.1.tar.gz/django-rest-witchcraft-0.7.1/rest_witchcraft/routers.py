# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from rest_framework import routers

from django_sorcery.db.meta import model_info


class DefaultRouter(routers.DefaultRouter):

    def get_default_base_name(self, viewset):

        model = getattr(viewset, "get_model", lambda: None)()

        assert model is not None, (
            "`base_name` argument not specified, and could not automatically determine the name from the viewset, "
            "as either queryset is is missing or is not a sqlalchemy query, or the serializer_class is not a "
            "sqlalchemy model serializer"
        )

        return model.__name__.lower()

    def get_lookup_regex(self, viewset, lookup_prefix=""):
        """
        Given a viewset, return the portion of the url regex that is used to match against a single instance.

        Can be overwritten by providing a `lookup_url_regex` on the viewset.
        """

        lookup_url_regex = getattr(viewset, "lookup_url_regex", None)
        if lookup_url_regex:
            return lookup_url_regex

        model = getattr(viewset, "get_model", lambda: None)()
        if model:
            info = model_info(model)
            base_regex = "(?P<{lookup_prefix}{lookup_url_kwarg}>{lookup_value})"

            regexes = []
            for key, _ in info.primary_keys.items():
                regexes.append(
                    base_regex.format(lookup_prefix=lookup_prefix, lookup_url_kwarg=key, lookup_value="[^/.]+")
                )

            return "/".join(regexes)

        return super(DefaultRouter, self).get_lookup_regex(viewset, lookup_prefix)
