# -*- coding: utf-8 -*-
# Core Django imports
from djstripe.models import Customer
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

# Imports from app
from .models import Agency, UserProfile, Team


class EmailBackend(ModelBackend):

    def authenticate(self, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            return None
        else:
            if (getattr(user, 'is_active', False)
                    and user.check_password(password)):
                return user
        return None


def create_user_profile(sender, user, request, **kwargs):
    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        user_profile = None

    split_email = user.email.split('@')
    agency_name = split_email[1].split('.')[0]
    agency_profile, created = Agency.objects.get_or_create(
        name=agency_name,
        email=split_email[1],
    )

    if created:
        agency_profile.administrators.add(user)
        agency_profile.save()

    if not user_profile and user.email:
        user_profile, created = UserProfile.objects.get_or_create(
            user=user,
        )
        if created:
            user_profile.employers.add(agency_profile)

            # Create team for user
            team = Team(name=agency_name, agency=agency_profile, max_members=1)
            team.save()

            # Add user as an admin
            team.admins.add(user)

            # Assign team to user_profile
            user_profile.team = team
            user_profile.save()
    else:
        user_profile.employers.add(agency_profile)
        user_profile.save()

    # Create Billing for user
    customer, created = Customer.get_or_create(subscriber=user)


def check_agency_auth_google_auth(strategy, details,
                                  user=None, *args, **kwargs):
    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        user_profile = None


    if user_profile and user_profile.google_id == '':
    	print 'test'
    	print kwargs['response']
    	if 'response' in kwargs and 'id' in kwargs['response']:
    		user_profile.google_id = kwargs['response']['id']
    		user_profile.save()


    if kwargs['is_new']:
	    # Find or create company domain
	    split_email = details['email'].split('@')
	    agency_name = split_email[1].split('.')[0]
	    agency_profile, created = Agency.objects.get_or_create(
	        name=agency_name,
	        email=split_email[1],
	    )

	    if created:
	        agency_profile.administrators.add(user)
	        agency_profile.save()

	    if not user_profile and details['email']:
	        user_profile, created = UserProfile.objects.get_or_create(
	            user=user,
	        )
	        if created:
	            user_profile.employers.add(agency_profile)

	            # Create Billing for user
	            customer, created = Customer.get_or_create(subscriber=user)

	            # Create team for user
	            team = Team(name=agency_name, agency=agency_profile, max_members=1)
	            team.save()

	            # Add user as an admin
	            team.admins.add(user)

	            # Assign team to user_profile
	            user_profile.team = team
	            user_profile.save()
	    else:
	        user_profile.employers.add(agency_profile)
	        user_profile.save()
