# -*- coding: utf-8 -*-
class disable_csrf(object):

	def process_request(self, request):
		setattr(request, '_dont_enforce_csrf_checks', True)
