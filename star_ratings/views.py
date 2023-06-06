from __future__ import unicode_literals

import copy

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect, JsonResponse
from django.views.generic import View

from . import app_settings
from .models import Rating
from .compat import is_authenticated
import json


class Rate(View):
    model = Rating

    def get_object(self):
        """
        Returns the model instance we're rating from the URL params.
        """
        content_type = ContentType.objects.get_for_id(self.kwargs.get('content_type_id'))
        return content_type.get_object_for_this_type(pk=self.kwargs.get('object_id'))

    def post(self, request, *args, **kwargs):
        def _post(request, *args, **kwargs):
            data = request.POST or json.loads(request.body.decode())
            
            data = copy.deepcopy(data)
            return_url = data.pop('next', '/')
            if type(return_url) == list:
                return_url = return_url[0]

            if 'HTTP_X_REAL_IP' in self.request.META:
                ip = self.request.META['HTTP_X_REAL_IP']
            else:
                ip = self.request.META['REMOTE_ADDR']
                
            score = data.get('score')
            data['user'] = is_authenticated(request.user) and request.user.pk or None
            try:
                rating = self.model.objects.rate(self.get_object(), score, user=data['user'], ip=ip)
                if request.is_ajax():
                    result = rating.to_dict()
                    result['user_rating'] = int(score)
                    return JsonResponse(data=result, status=200)
                else:
                    return HttpResponseRedirect(return_url)
            except ValidationError as err:
                if request.is_ajax():
                    return JsonResponse(data={'error': err.message}, status=400)
                else:
                    return HttpResponseRedirect(return_url)

        if not app_settings.STAR_RATINGS_ANONYMOUS:
            return login_required(_post)(request, *args, **kwargs)

        return _post(request, *args, **kwargs)
