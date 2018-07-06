# -*- coding: utf-8 -*-
# Python imports
import uuid

# Core Django imports
from django.core import signing
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404

# Third-party app imports
from django_filters.rest_framework import DjangoFilterBackend
from registration.signals import user_registered
from registration.views import RegistrationView as BaseRegistrationView
from rest_framework.decorators import list_route, detail_route
from rest_framework.exceptions import (
	NotAuthenticated,
	PermissionDenied,
	ParseError,
)

# Imports from app
from tabulae.apps.general.viewset import NewsAIModelViewSet
from tabulae.apps.general.response import Response, BulkResponse
from .models import (
	UserProfile,
	Billing,
	Agency,
	Client,
	Team,
	EmailCode,
	Invite,
)

from .serializers import (
	UserSerializer,
	AgencySerializer,
	ClientSerializer,
	TeamSerializer,
	InviteSerializer,
	UserLiveTokenSerializer,
)

from .permissions import (
	IsAdminOrIsSelf,
	UserPermission,
	AgencyPermission,
	ClientPermission,
	TeamPermission,
	InvitePermission,
)

REGISTRATION_SALT = getattr(settings, 'REGISTRATION_SALT', 'registration')


class RegistrationView(BaseRegistrationView):
	"""
	Register a new (inactive) user account, generate an activation key
	and email it to the user.
	This is different from the model-based activation workflow in that
	the activation key is the username, signed using Django's
	TimestampSigner, with HMAC verification on activation.
	"""
	email_body_template = 'registration/activation_email.txt'
	email_subject_template = 'registration/activation_email_subject.txt'

	def register(self, form):
		new_user = self.create_inactive_user(form)
		user_registered.send(sender=self.__class__,
							 user=new_user,
							 request=self.request)
		return new_user

	def get_success_url(self, user):
		return ('registration_complete', (), {})

	def create_inactive_user(self, form):
		"""
		Create the inactive user account and send an email containing
		activation instructions.
		"""
		new_user = form.save(commit=False)
		new_user.is_active = False
		new_user.save()

		self.send_activation_email(new_user)

		return new_user

	def get_activation_key(self, user):
		"""
		Generate the activation key which will be emailed to the user.
		"""
		return signing.dumps(
			obj=getattr(user, user.USERNAME_FIELD),
			salt=REGISTRATION_SALT
		)

	def get_email_context(self, activation_key):
		"""
		Build the template context used for the activation email.
		"""
		return {
			'activation_key': activation_key,
			'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
			'site': get_current_site(self.request)
		}

	def send_activation_email(self, user):
		"""
		Send the activation email. The activation key is the username,
		signed using TimestampSigner.
		"""
		activation_key = self.get_activation_key(user)
		context = self.get_email_context(activation_key)
		context.update({
			'user': user
		})
		subject = render_to_string(self.email_subject_template,
								   context)
		# Force subject to a single line to avoid header-injection
		# issues.
		subject = ''.join(subject.splitlines())
		message = render_to_string(self.email_body_template,
								   context)
		user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)


class UserViewSet(NewsAIModelViewSet):
	serializer_class = UserSerializer
	permission_classes = (UserPermission,)
	filter_backends = (DjangoFilterBackend,)

	add_email_body_template = 'add_email/email.txt'
	add_email_subject_template = 'add_email/email_subject.txt'

	def get_user_by_pk(self, request, pk):
		if request.user and request.user.is_authenticated():
			user = None
			if pk == 'me':
				user = request.user
			else:
				UserModel = get_user_model()
				user = UserModel.objects.get(pk=pk)
				requested_user_profile = UserProfile.objects.get(user=user)

				loggedin_user_profile = UserProfile.objects.get(user=request.user)

				if loggedin_user_profile.team != requested_user_profile.team:
					raise PermissionDenied()
			return user
		raise NotAuthenticated()

	def retrieve(self, request, pk=None):
		if request.user and request.user.is_authenticated():
			user = self.get_user_by_pk(request, pk)
			serializer = UserSerializer(user)
			return Response(serializer.data, {})
		raise NotAuthenticated()

	def list(self, request):
		if request.user and request.user.is_authenticated():
			if request.user.is_staff:
				queryset = self.filter_queryset(self.get_queryset())

				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page, many=True)
					return self.get_paginated_response(serializer.data)

				serializer = self.get_serializer(queryset, many=True)
				return BulkResponse(serializer.data, {},
									len(serializer.data), len(serializer.data))
			raise PermissionDenied()
		raise NotAuthenticated()

	def setup_email_context(self, user):
		return {
			'user': user,
			'site': get_current_site(self.request),
		}

	def send_add_email(self, user, email_code):
		context = self.setup_email_context(user)
		context.update({
			'email_code': email_code,
		})
		subject = render_to_string(self.add_email_subject_template,
								   context)
		subject = ''.join(subject.splitlines())
		message = render_to_string(self.add_email_body_template,
								   context)
		send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
				  [email_code.email])

	# GET /users or /users/<id> (External)
	def get_queryset(self,):
		UserModel = get_user_model()
		if self.request.user and self.request.user.is_authenticated():
			return UserModel.objects.all().order_by('-date_joined')
		raise NotAuthenticated()

	# GET /users/<id> if id == 'me' (External)
	@list_route(methods=['get', 'patch'])
	def me(self, request):
		if request.user and request.user.is_authenticated():
			if request.method == 'GET':
				serializer = UserSerializer(self.request.user)
				return Response(serializer.data, {})
			elif request.method == 'PATCH':
				user_profile = UserProfile.objects.get(user=request.user)
				if ('emailsignatures' in request.data):
					user_profile.email_signatures = request.data['emailsignatures']
				if ('emailsignature' in request.data):
					user_profile.email_signature = request.data['emailsignature']

				user_profile.save()
				serializer = UserSerializer(self.request.user)
				return Response(serializer.data, {})
		raise NotAuthenticated

	# GET /users/<id>/live-token (External)
	@detail_route(methods=['get'], url_path='live-token',
				  permission_classes=[IsAdminOrIsSelf])
	def live_token(self, request, pk=None):
		user = self.get_user_by_pk(request, pk)
		user_profile = UserProfile.objects.get(user=user)

		serializer = UserLiveTokenSerializer(user_profile)
		return Response(serializer.data, {})

	# GET /users/<id>/confirm-email (External)
	@detail_route(methods=['get'], url_path='confirm-email',
				  permission_classes=[IsAdminOrIsSelf])
	def confirm_email(self, request, pk=None):
		user = self.get_user_by_pk(request, pk)
		user_profile = UserProfile.objects.get(user=user)
		code = request.query_params.get('code')
		if code:
			email_code = EmailCode.objects.get(invite_code=code)
			if email_code:
				# if email_code exists then we want to save the
				# email address to the user, and save the
				# user.
				if not user_profile.sendgrid_emails:
					user_profile.sendgrid_emails = []
				user_profile.sendgrid_emails.append(email_code.email)
				user_profile.sendgrid_emails = list(
					set(user_profile.sendgrid_emails))
				user_profile.save()

				# Delete email_code
				email_code.delete()

				serializer = UserSerializer(self.request.user)
				return Response(serializer.data, {})
			raise NotFound()
		raise ParseError()

	# GET /users/<id>/plan-details (External)
	@detail_route(methods=['get'], url_path='plan-details',
				  permission_classes=[IsAdminOrIsSelf])
	def plan_details(self, request, pk=None):
		user = self.get_user_by_pk(request, pk)
		user_profile = UserProfile.objects.get(user=user)

		return Response({
			'planname': 'Growing Business',
			'emailaccounts': 10,
			'dailyemailsallowed': 10000,
			'emailssenttoday': 7,
			'ontrial': False
		}, {})

	# GET /users/<id>/remove-integrations (External)
	@detail_route(methods=['get'], url_path='remove-integrations',
				  permission_classes=[IsAdminOrIsSelf])
	def remove_integration(self, request, pk=None):
		if self.request.user and self.request.user.is_authenticated():
			user = self.get_user_by_pk(request, pk)
			user_profile = UserProfile.objects.get(user=user)

			user_profile.gmail = False
			user_profile.outlook = False
			user_profile.external_email = False
			user_profile.save()

			serializer = UserSerializer(self.request.user)
			return Response(serializer.data, {})

		raise NotAuthenticated

	# GET /users/<id>/campaigns (Internal)

	# GET /users/<id>/profile (Internal)

	# GET /users/<id>/ban (Internal)

	# POST /users/<id>/feedback (External)
	@detail_route(methods=['post'], url_path='feedback',
				  permission_classes=[IsAdminOrIsSelf])
	def feedback(self, request, pk=None):
		user = self.get_user_by_pk(request, pk)
		user_profile = UserProfile.objects.get(user=user)

		if 'reason' in request.data and 'feedback' in request.data:
			user_profile.trial_expire_reason = request.data['reason']
			user_profile.trial_expire_feedback = request.data['feedback']
			user_profile.save()

			serializer = UserSerializer(self.request.user)
			return Response(serializer.data, {})
		raise ParseError()

	# POST /users/<id>/add-email (External)
	@detail_route(methods=['post'], url_path='add-email',
				  permission_classes=[IsAdminOrIsSelf])
	def add_email(self, request, pk=None):
		user = self.get_user_by_pk(request, pk)
		user_profile = UserProfile.objects.get(user=user)

		if 'email' in request.data:
			email = request.data['email']
			# Check if it already exists in user
			# if (email in user_profile.sendgrid_emails or user.email ==
			# email):

			# Create an email code object with
			# an invitation code to send to the user
			email_code = EmailCode(invite_code=str(uuid.uuid4()),
								   email=str(request.data['email']),
								   created_by=user)
			email_code.save()

			# Send user email
			self.send_add_email(user, email_code)

			# Return user profile
			serializer = UserSerializer(self.request.user)
			return Response(serializer.data, {})
		raise ParseError()

	# POST /users/<id>/change-name (External)
	@detail_route(methods=['post'], url_path='change-name',
				  permission_classes=[IsAdminOrIsSelf])
	def change_name(self, request, pk=None):
		user = self.get_user_by_pk(request, pk)

		change = False
		if 'firstname' in request.data:
			user.first_name = request.data['firstname']
			change = True

		if 'lastname' in request.data:
			user.last_name = request.data['lastname']
			change = True

		if change:
			user.save()

		serializer = UserSerializer(self.request.user)
		return Response(serializer.data, {})

	# POST /users/<id>/remove-email (External)
	@detail_route(methods=['post'], url_path='remove-email',
				  permission_classes=[IsAdminOrIsSelf])
	def remove_email(self, request, pk=None):
		user = self.get_user_by_pk(request, pk)
		user_profile = UserProfile.objects.get(user=user)

		if 'email' in request.data:
			if request.data['email'] in user_profile.sendgrid_emails:
				user_profile.sendgrid_emails.remove(request.data['email'])
				user_profile.sendgrid_emails = list(
					set(user_profile.sendgrid_emails))
				user_profile.save()

				serializer = UserSerializer(self.request.user)
				return Response(serializer.data, {})
		raise ParseError()

	# POST /users/<id>/add-plan (Internal)

	# POST /users/<id>/profile (Internal)

	# POST /users/<id>/change-email (Internal)

	# PATCH /users/<id>/profile (Internal)


class AgencyViewSet(NewsAIModelViewSet):
	serializer_class = AgencySerializer
	permission_classes = (AgencyPermission,)
	filter_backends = (DjangoFilterBackend,)

	def get_agency_by_pk(self, request, pk):
		# Switch to team__pk=request.user.team.pk
		queryset = Agency.objects.filter(created_by=request.user)
		agency = get_object_or_404(queryset, pk=pk)
		return agency

	def retrieve(self, request, pk=None):
		if request.user and request.user.is_authenticated():
			agency = self.get_agency_by_pk(request, pk)
			serializer = AgencySerializer(agency)
			return Response(serializer.data, {})
		raise NotAuthenticated()

	def list(self, request):
		queryset = self.filter_queryset(self.get_queryset())

		page = self.paginate_queryset(queryset)
		if page is not None:
			serializer = self.get_serializer(page, many=True)
			return self.get_paginated_response(serializer.data)

		serializer = self.get_serializer(queryset, many=True)
		return BulkResponse(serializer.data, {},
							len(serializer.data), len(serializer.data))

	def get_queryset(self,):
		if self.request.user and self.request.user.is_authenticated():
			return Agency.objects.all().order_by('-created')
		raise NotAuthenticated()

	def get_serializer(self, *args, **kwargs):
		if 'data' in kwargs:
			data = kwargs['data']

			if isinstance(data, list):
				kwargs['many'] = True

		return super(AgencyViewSet, self).get_serializer(*args, **kwargs)


class ClientViewSet(NewsAIModelViewSet):
	serializer_class = ClientSerializer
	permission_classes = (ClientPermission,)
	filter_backends = (DjangoFilterBackend,)

	def get_client_by_pk(self, request, pk):
		# Switch to team__pk=request.user.team.pk
		queryset = Client.objects.filter(created_by=request.user)
		client = get_object_or_404(queryset, pk=pk)
		return client

	def retrieve(self, request, pk=None):
		if request.user and request.user.is_authenticated():
			client = self.get_client_by_pk(request, pk)
			serializer = ClientSerializer(client)
			return Response(serializer.data, {})
		raise NotAuthenticated()

	def list(self, request):
		queryset = self.filter_queryset(self.get_queryset())

		page = self.paginate_queryset(queryset)
		if page is not None:
			serializer = self.get_serializer(page, many=True)
			return self.get_paginated_response(serializer.data)

		serializer = self.get_serializer(queryset, many=True)
		return BulkResponse(serializer.data, {},
							len(serializer.data), len(serializer.data))

	def get_queryset(self,):
		if self.request.user and self.request.user.is_authenticated():
			return Client.objects.filter(
				created_by=self.request.user,).order_by('-created')
		raise NotAuthenticated()

	def get_serializer(self, *args, **kwargs):
		if 'data' in kwargs:
			data = kwargs['data']

			if isinstance(data, list):
				kwargs['many'] = True

		return super(ClientViewSet, self).get_serializer(*args, **kwargs)


class TeamViewSet(NewsAIModelViewSet):
	serializer_class = TeamSerializer
	permission_classes = (TeamPermission,)
	filter_backends = (DjangoFilterBackend,)

	def get_team_by_pk(self, request, pk):
		# Switch to team__pk=request.user.team.pk
		queryset = Team.objects.all()
		client = get_object_or_404(queryset, pk=pk)
		return client

	def retrieve(self, request, pk=None):
		if request.user and request.user.is_authenticated():
			team = self.get_team_by_pk(request, pk)
			serializer = TeamSerializer(team)
			return Response(serializer.data, {})
		raise NotAuthenticated()

	def list(self, request):
		if request.user and request.user.is_authenticated():
			if request.user.is_staff:
				queryset = self.filter_queryset(self.get_queryset())

				page = self.paginate_queryset(queryset)
				if page is not None:
					serializer = self.get_serializer(page, many=True)
					return self.get_paginated_response(serializer.data)

				serializer = self.get_serializer(queryset, many=True)
				return BulkResponse(serializer.data, {},
									len(serializer.data), len(serializer.data))
			raise PermissionDenied()
		raise NotAuthenticated()

	def get_queryset(self,):
		if self.request.user and self.request.user.is_authenticated():
			return Team.objects.all().order_by('-created')
		raise NotAuthenticated()

	def get_serializer(self, *args, **kwargs):
		if 'data' in kwargs:
			data = kwargs['data']

			if isinstance(data, list):
				kwargs['many'] = True

		return super(TeamViewSet, self).get_serializer(*args, **kwargs)


class InviteViewSet(NewsAIModelViewSet):
	serializer_class = InviteSerializer
	permission_classes = (InvitePermission,)
	filter_backends = (DjangoFilterBackend,)

	def get_invite_by_pk(self, request, pk):
		# Switch to team__pk=request.user.team.pk
		queryset = Invite.objects.filter(created_by=request.user)
		invite = get_object_or_404(queryset, pk=pk)
		return invite

	def retrieve(self, request, pk=None):
		if request.user and request.user.is_authenticated():
			invite = self.get_invite_by_pk(request, pk)
			serializer = InviteSerializer(invite)
			return Response(serializer.data, {})
		raise NotAuthenticated()

	def list(self, request):
		queryset = self.filter_queryset(self.get_queryset())

		page = self.paginate_queryset(queryset)
		if page is not None:
			serializer = self.get_serializer(page, many=True)
			return self.get_paginated_response(serializer.data)

		serializer = self.get_serializer(queryset, many=True)
		return BulkResponse(serializer.data, {},
							len(serializer.data), len(serializer.data))

	def get_queryset(self,):
		if self.request.user and self.request.user.is_authenticated():
			return Invite.objects.all().order_by('-created')
		raise NotAuthenticated()

	def get_serializer(self, *args, **kwargs):
		if 'data' in kwargs:
			data = kwargs['data']

			if isinstance(data, list):
				kwargs['many'] = True

		return super(InviteViewSet, self).get_serializer(*args, **kwargs)
