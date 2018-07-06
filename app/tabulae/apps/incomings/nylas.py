# -*- coding: utf-8 -*-
import json
import datetime

# Core Django imports
from django.http import HttpResponse

# Imports from app
from tabulae.apps.emails.models import Email, Campaign


def NylasMessageIncomingView(request):
    challenge = request.GET.get('challenge', '')
    if challenge != '':
        return HttpResponse(challenge)
    '''
    created:
    {
        u'date': 1510261153,
        u'object': u'message',
        u'type': u'message.created',
        u'object_data': {
            u'namespace_id': u'1v9ipj1d2z8jaq3elmqswmraw',
            u'account_id': u'1v9ipj1d2z8jaq3elmqswmraw',
            u'object': u'message',
            u'attributes': {
                u'thread_id': u'35klqcooi7t5dyrdtu4lo7htk',
                u'received_date': 1510261149
            },
            u'id': u'3ae7ijlj5qwvpkzr0reno6dx6',
            u'metadata': None
        }
    }

    ---

    opened:

    {
        u'date': 1510264477,
        u'object': u'metadata',
        u'type': u'message.opened',
        u'object_data': {
            u'namespace_id': u'5k3rl5bw4elb4n3gb2xayo2m8',
            u'account_id': u'5k3rl5bw4elb4n3gb2xayo2m8',
            u'object': u'metadata',
            u'attributes': None,
            u'id': u'5taidhabfphxdc2lk7ybjadq3',
            u'metadata': {
                u'count': 1,
                u'sender_app_id': 23729,
                u'recents': [{
                    u'ip': u'66.102.8.56',
                    u'user_agent': u'Mozilla/5.0 (Windows NT 5.1; rv:11.0) Gecko Firefox/11.0 (via ggpht.com GoogleImageProxy)',
                    u'id': 0
                }],
                u'message_id': u'b02rd34tyqbtmrav4apmeyhkt',
                u'payload': u'60'
            }
        }
    }

    ---

    clicked:

    {
        u'date': 1510264566,
        u'object': u'metadata',
        u'type': u'message.link_clicked',
        u'object_data': {
            u'namespace_id': u'5k3rl5bw4elb4n3gb2xayo2m8',
            u'account_id': u'5k3rl5bw4elb4n3gb2xayo2m8',
            u'object': u'metadata',
                u'attributes': None,
                u'id': u'1ohwc6n13bjfctyo6rzoy9cb7',
                u'metadata': {
                    u'sender_app_id': 23729,
                    u'message_id': u'b02rd34tyqbtmrav4apmeyhkt',
                    u'payload': u'60',
                    u'link_data': [{
                        u'url': u'https://email2.newsai.co/a?id=5762567494434816&url=https://www.newsai.co/',
                    u'count': 2
                }],
                u'recents': [{
                    u'ip': u'196.52.2.92',
                    u'link_index': 0,
                    u'user_agent': u'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36',
                    u'id': 0
                }, {
                    u'ip': u'196.52.2.92',
                    u'link_index': 0,
                    u'user_agent': u'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36',
                    u'id': 1
                }]
            }
        }
    }

    ---

    reply:

    {
        u'date': 1510265015,
        u'object': u'message',
        u'type': u'thread.replied',
        u'object_data': {
            u'namespace_id': u'1v9ipj1d2z8jaq3elmqswmraw',
            u'account_id': u'1v9ipj1d2z8jaq3elmqswmraw',
            u'object': u'message',
            u'attributes': None,
            u'id': u'7z1frdnm3udn7qhj8cvgq5ou7',
            u'metadata': {
                u'sender_app_id': 23729,
                u'timestamp': 1510265011,
                u'from_self': False,
                u'message_id': u'7z1frdnm3udn7qhj8cvgq5ou7',
                u'thread_id': u'd1brozrc1wo0k39ev8miogadg',
                u'reply_to_message_id': u'dxnyact9wyinz3jsr3i6r8n15',
                u'payload': u'63'
            }
        }
    }

    '''

    resp = json.loads(request.body)
    if 'deltas' in resp:
        for delta in resp['deltas']:
            if ('type' in delta and
                    'object_data' in delta and
                    'metadata' in delta['object_data'] and
                    'payload' in delta['object_data']['metadata']):
                try:
                    # Get email
                    email = Email.objects.get(pk=delta['object_data'][
                        'metadata']['payload'])

                    # Get campaign
                    today = datetime.datetime.now().date()
                    tomorrow = today + datetime.timedelta(1)
                    today_start = datetime.datetime.combine(
                        today, datetime.time())
                    today_end = datetime.datetime.combine(
                        tomorrow, datetime.time())

                    campaigns = Campaign.objects.filter(
                        created__lte=today_end,
                        created__gte=today_start,
                        created_by=email.created_by,
                        subject=email.subject)

                    # Conditions
                    if delta['type'] == 'message.opened':
                        first_time_opened = False

                        if email.opened == 0:
                            first_time_opened = True

                        email.opened += 1
                        email.save()

                        if campaigns.count() > 0:
                            campaigns = campaigns.all()
                            campaign = campaigns[0]

                            # Increase opens
                            campaign.opens += 1

                            # Increase unique opens
                            if first_time_opened:
                                campaign.unique_opens += 1

                            campaign.save()
                    elif delta['type'] == 'message.link_clicked':
                        first_time_clicked = False

                        if email.clicked == 0:
                            first_time_clicked = True

                        email.clicked += 1
                        email.save()

                        if campaigns.count() > 0:
                            campaigns = campaigns.all()
                            campaign = campaigns[0]

                            # Increase click
                            campaign.clicks += 1

                            # Increase unique clicks
                            if first_time_clicked:
                                campaign.unique_clicks += 1

                            campaign.save()
                    elif delta['type'] == 'thread.replied':
                        first_time_replied = False

                        if email.replies == 0:
                            first_time_replied = True

                        email.replies += 1
                        email.save()

                        if campaigns.count() > 0:
                            campaigns = campaigns.all()
                            campaign = campaigns[0]

                            # Increase replies
                            campaign.replies += 1

                            # Increase unique replies
                            if first_time_replied:
                                campaign.unique_replies += 1

                            campaign.save()
                    elif delta['type'] == 'message.created':
                        pass
                except Email.DoesNotExist:
                    print 'Error'
                    continue

    return HttpResponse()
