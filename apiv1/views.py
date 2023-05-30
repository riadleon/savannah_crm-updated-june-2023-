import datetime
import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django import forms
from django.contrib import messages

from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from corm.models import Source, Channel, Member, Contact, Conversation, Contribution, Event
from frontendv2.views import SavannahView

from .serializers import SourceSerializer, IdentitySerializer, ConversationSerializer, ContributionSerializer, ZapierIdentitySerializer, EventSerializer, EventAttendeeSerializer
from .icons import generic_icons, brand_icons

# Create your views here.
class APISourceForm(forms.ModelForm):
    class Meta:
        model = Source
        fields = ['name', 'icon_name']
        labels = {
            'icon_name': 'Icon',
        }
        widgets = {
            'icon_name': forms.Select(),
        }
        

class SourceAdd(SavannahView):
    def _add_sources_message(self):
        pass

    def as_view(request):
        view = SourceAdd(request, community_id=request.session['community'])

        new_source = Source(community=view.community, connector="corm.plugins.api", api_key=uuid.uuid4())

        if request.method == "POST":
            form = APISourceForm(data=request.POST, instance=new_source)
            if form.is_valid():
                source = form.save()
                messages.success(request, 'Your API Integration source has been created. You can <a href="https://docs.savannahhq.com/api/" target="savannah_docs">start using it</a> with the authentication token below.')
                return redirect('channels', community_id=view.community.id, source_id=source.id)

        icon_choices = [
            ('fas fa-cogs', 'Custom Integration'),
            ('Generic Icons', [('fas fa-%s' % icon, icon.title()) for icon in generic_icons]),
            ('Brand Icons', [('fab fa-%s' % icon, icon.title()) for icon in brand_icons]),
        ]

        form = APISourceForm(instance=new_source)
        form.fields['icon_name'].widget.choices = icon_choices
        
        context = view.context
        context.update({
            "source_form": form,
            'source_plugin': 'API Integration',
            'submit_text': 'Add',
            'submit_class': 'btn btn-success',
        })
        return render(request, "savannahv2/source_add.html", context)

class SourceTokenAuthentication(BaseAuthentication):
    def authenticate_header(self, request):
        return "Authorization"

    def authenticate(self, request):
        try:
            token = request.GET['auth_token']
        except KeyError:
            auth = request.META.get('HTTP_AUTHORIZATION', '').split(" ")
            if not auth or auth[0].lower() != 'token':
                return None

            if len(auth) == 1:
                msg = 'Invalid token header. No credentials provided.'
                raise AuthenticationFailed(msg)
            elif len(auth) > 2:
                msg = 'Invalid token header. Token string should not contain spaces.'
                raise AuthenticationFailed(msg)

            try:
                token = str(auth[1])
            except UnicodeError:
                msg = 'Invalid token header. Token string should not contain invalid characters.'
                raise AuthenticationFailed(msg)

        source = None
        try:
            source = Source.objects.get(connector="corm.plugins.api", api_key=token, enabled=True)
        except Source.DoesNotExist:
            msg = 'Invalid token. Token is not associated with any API Integration'
            raise AuthenticationFailed(msg)

        request.source = source
        return (source.community.owner, token)

class SavannahIntegrationView(APIView):
    authentication_classes = [SourceTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]


class SourceInfo(SavannahIntegrationView):
    """
    Returns information about the Source for this API token
    """

    def get(self, request, format=None):
        serializer = SourceSerializer(request.source, many=False)
        return Response(serializer.data)

class IdentityList(SavannahIntegrationView):
    """
    List all identities, or create a new identity.
    """

    def get(self, request, format=None):
        identities = Contact.objects.filter(source=request.source).select_related('member').prefetch_related('member__tags')
        serializer = IdentitySerializer(identities, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = IdentitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(source=request.source)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ZapierIdentityList(SavannahIntegrationView):
    """
    List all identities with zapier id field
    """

    def get(self, request, format=None):
        identities = Contact.objects.filter(source=request.source).select_related('member').order_by('-member__last_seen')
        serializer = ZapierIdentitySerializer(identities, many=True)
        return Response(serializer.data)


class IdentityDetail(SavannahIntegrationView):
    """
    Retrieve, update or delete a Member identity instance.
    """
    def get(self, request, origin_id, format=None):
        identity = get_object_or_404(Contact, source=request.source, origin_id=origin_id)
        serializer = IdentitySerializer(identity)
        return Response(serializer.data)

    def put(self, request, origin_id, format=None):
        identity = get_object_or_404(Contact, source=request.source, origin_id=origin_id)
        serializer = IdentitySerializer(identity, data=request.data)
        if serializer.is_valid():
            serializer.save(source=request.source)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ConversationsList(SavannahIntegrationView):
    """
    Create new Conversation records
    """

    def get(self, request, format=None):
        convos = Conversation.objects.filter(channel__source=request.source)
        serializer = ConversationSerializer(convos, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ConversationSerializer(data=request.data)
        if serializer.is_valid():
            convo = serializer.save(source=request.source)
            return Response(ConversationSerializer(convo).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ContributionsList(SavannahIntegrationView):
    """
    Create new Contribution records
    """

    def get(self, request, format=None):
        contribs = Contribution.objects.filter(channel__source=request.source)
        serializer = ContributionSerializer(contribs, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ContributionSerializer(data=request.data)
        if serializer.is_valid():
            contrib = serializer.save(source=request.source)
            return Response(ContributionSerializer(contrib).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EventsList(SavannahIntegrationView):
    """
    Create new Event records
    """

    def get(self, request, format=None):
        events = Event.objects.filter(source=request.source)
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            event = serializer.save(source=request.source)
            return Response(EventSerializer(event).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EventAttendeesList(SavannahIntegrationView):
    """
    Create new Event records
    """

    def get(self, request, event_id, format=None):
        event = Event.objects.get(source=request.source, origin_id=event_id)
        contacts = Contact.objects.filter(source=request.source, member__event_attendance__event=event)
        contacts = contacts.select_related('member').prefetch_related('member__tags')
        serializer = EventAttendeeSerializer(contacts, many=True)
        return Response(serializer.data)

    def post(self, request, event_id, format=None):
        event = Event.objects.get(source=request.source, origin_id=event_id)
        serializer = EventAttendeeSerializer(data=request.data)
        if serializer.is_valid():
            attendee_contact = serializer.save(source=request.source, event=event)
            return Response(EventAttendeeSerializer(attendee_contact).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

