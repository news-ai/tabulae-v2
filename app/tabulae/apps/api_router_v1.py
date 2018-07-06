# -*- coding: utf-8 -*-
# Third-party app imports
from rest_framework.routers import Route, DynamicListRoute, DynamicDetailRoute, SimpleRouter

# Imports from app
from .users.views import (
    UserViewSet,
    AgencyViewSet,
    ClientViewSet,
    TeamViewSet,
    InviteViewSet,
)
from .feeds.views import FeedViewSet
from .contacts.views import ContactViewSet
from .lists.views import MediaListViewSet
from .templates.views import TemplateViewSet
from .emails.views import EmailViewSet
from .publications.views import PublicationViewSet
from .files.views import FileViewSet
from .database_contacts.views import DatabaseContactViewSet
from .database_publications.views import DatabasePublication


class CustomRouter(SimpleRouter):
    routes = [
        # List route.
        Route(
            url=r'^{prefix}{trailing_slash}$',
            mapping={
                'get': 'list',
                'post': 'create',
                'patch': 'bulk_update'
            },
            name='{basename}-list',
            initkwargs={'suffix': 'List'}
        ),
        # Dynamically generated list routes.
        # Generated using @list_route decorator
        # on methods of the viewset.
        DynamicListRoute(
            url=r'^{prefix}/{methodname}{trailing_slash}$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
        # Detail route.
        Route(
            url=r'^{prefix}/{lookup}{trailing_slash}$',
            mapping={
                'get': 'retrieve',
                'put': 'update',
                'patch': 'partial_update',
                'delete': 'destroy'
            },
            name='{basename}-detail',
            initkwargs={'suffix': 'Instance'}
        ),
        # Dynamically generated detail routes.
        # Generated using @detail_route decorator on methods of the viewset.
        DynamicDetailRoute(
            url=r'^{prefix}/{lookup}/{methodname}{trailing_slash}$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
    ]


router = CustomRouter()
# General routes
router.register(r'users', UserViewSet, base_name='user')
router.register(r'agencies', AgencyViewSet, base_name='agency')
router.register(r'clients', ClientViewSet, base_name='client')
router.register(r'teams', TeamViewSet, base_name='team')
router.register(r'invites', InviteViewSet, base_name='invite')

# Tabulae routes
router.register(r'publications', PublicationViewSet, base_name='publication')
router.register(r'contacts', ContactViewSet, base_name='contact')
router.register(r'files', FileViewSet, base_name='file')
router.register(r'lists', MediaListViewSet, base_name='list')
router.register(r'emails', EmailViewSet, base_name='email')
# email-settings
router.register(r'templates', TemplateViewSet, base_name='template')
router.register(r'feeds', FeedViewSet, base_name='feed')

# Media database routes
router.register(r'database-contacts', DatabaseContactViewSet,
                base_name='database-contact')
router.register(r'database-publications', DatabasePublication,
                base_name='database-publication')
