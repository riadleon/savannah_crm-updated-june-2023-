import operator
from functools import reduce
import datetime, calendar
import dateutil.parser

import json
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.db.models import F, Q, Count, Max
from django.contrib import messages
from django.http import JsonResponse, Http404
from django import forms
from django.contrib.auth import authenticate, login as login_user, logout as logout_user
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.views import PasswordResetView as DjangoPasswordResetView

from corm.models import *
from corm.connectors import ConnectionManager

from frontendv2.views import SavannahView
from frontendv2.models import ManagerInvite, PublicDashboard
from frontendv2.views.charts import PieChart
from frontendv2 import colors

class PublicReportForm(forms.ModelForm):
    class Meta:
        model = PublicDashboard
        fields = [
            'display_name', 
            'show_companies', 
            'show_members', 
        ]

class Reports(SavannahView):
    def __init__(self, request, community_id):
        super().__init__(request, community_id)
        self.active_tab = "reports"

    def all_reports(self):
        return Report.objects.filter(community=self.community).order_by('-generated')

    @login_required
    def as_view(request, community_id):
        view = Reports(request, community_id)
        if request.method == "POST":
            pass
        return render(request, "savannahv2/reports.html", view.context)

def view_report(request, community_id, report_id):
    report = get_object_or_404(Report, id=report_id)
    if report.report_type == Report.GROWTH:
        return GrowthReport.as_view(request, community_id, report)
    elif report.report_type == Report.ANNUAL:
        return AnnualReport.as_view(request, community_id, report)
    else:
        messages.error(request, "Unknown report type: %s" % self.report.report_type)
        return redirect('reports', community_id=community_id)

def publish_report(request, community_id, report_id):
    report = get_object_or_404(Report, id=report_id)
    if report.report_type == Report.GROWTH:
        return GrowthReport.publish(request, community_id, report)
    elif report.report_type == Report.ANNUAL:
        return AnnualReport.publish(request, community_id, report)
    else:
        messages.error(request, "Unknown report type: %s" % report.report_type)
        return redirect('reports', community_id=community_id)

def view_public_report(request, dashboard_id):
    dashboard = get_object_or_404(PublicDashboard, id=dashboard_id)
    report_id = dashboard.filters.get('report_id')

    report = get_object_or_404(Report, id=report_id)
    if report.report_type == Report.GROWTH:
        return GrowthReport.public(request, dashboard.community.id, report, dashboard)
    elif report.report_type == Report.ANNUAL:
        return AnnualReport.public(request, dashboard.community.id, report, dashboard)
    else:
        raise Http404

class GrowthReport(SavannahView):
    def __init__(self, request, community_id, report):
        super().__init__(request, community_id)
        self.active_tab = "reports"
        self.report = report
        self.data = json.loads(self.report.data)
        self.charts = set()
        self.previous_company_activity = dict()
        self.previous_company_contributions = dict()
        try:
            self.previous = Report.objects.filter(community=self.report.community, report_type=Report.GROWTH, generated__lt=report.generated).order_by('-generated')[0]
            self.previous_data = json.loads(self.previous.data)
            if 'top_company_activity' in self.previous_data:
                for company in self.previous_data['top_company_activity']:
                    self.previous_company_activity[company['company_id']] = company['conversations']
            if 'top_company_contributions' in self.previous_data:
                for company in self.previous_data['top_company_contributions']:
                    self.previous_company_contributions[company['company_id']] = company['contributions']
        except:
            self.previous = None
            self.previous_data = None

    @property
    def start(self):
        return self.data['start']
        
    @property
    def end(self):
        return self.data['end']
        
    @property
    def month_name(self):
        return calendar.month_name[self.report.generated.month]
        
    @property
    def previous_month_name(self):
        if self.previous is None:
            return "Previous"
        return calendar.month_name[self.previous.generated.month]
        
    @property
    def new_member_count(self):
        return len(self.data['new_members'])

    @property 
    def new_member_diff(self):
        if self.previous is None:
            return 0
        if len(self.previous_data['new_members']) == 0:
            return 0
        diff = len(self.data['new_members']) - len(self.previous_data['new_members'])
        return 100 * diff / len(self.previous_data['new_members'])

    @property 
    def active_member_diff(self):
        if self.previous is None:
            return 0
        previous_activity = 0
        for activity in self.previous_data['member_activity']['active']:
            previous_activity += activity
        if previous_activity == 0:
            return 0
        new_activity = 0
        for activity in self.data['member_activity']['active']:
            new_activity += activity
        diff = new_activity - previous_activity
        return 100 * diff / previous_activity

    @property
    def new_contributor_count(self):
        return len(self.data['new_contributors'])
        
    @property 
    def new_contributor_diff(self):
        if self.previous is None:
            return 0
        if len(self.previous_data['new_contributors']) == 0:
            return 0
        diff = len(self.data['new_contributors']) - len(self.previous_data['new_contributors'])
        return 100 * diff / len(self.previous_data['new_contributors'])

    @property
    def new_members(self):
        for member in self.data['new_members']:
            member['joined'] = dateutil.parser.parse(member["joined"])
            yield(member)

    @property
    def new_contributors(self):
        for member in self.data['new_contributors']:
            member['first_contrib'] = dateutil.parser.parse(member["first_contrib"])
            yield(member)

    @property
    def top_contributors(self):
        for member in self.data['top_contributors']:
            yield(member)

    @property
    def top_supporters(self):
        for member in self.data['top_supporters']:
            yield(member)

    @property
    def has_company_data(self):
        return 'top_company_contributions' in self.data or 'top_company_activity' in self.data

    @property
    def top_company_activity(self):
        for company in self.data.get('top_company_activity', []):
            if company['company_id'] in self.previous_company_activity:
                company['diff'] = 100 * (company.get('conversations', 0) - self.previous_company_activity[company['company_id']]) / self.previous_company_activity[company['company_id']]
            yield(company)

    @property
    def top_company_contributions(self):
        for company in self.data.get('top_company_contributions', []):
            if company['company_id'] in self.previous_company_contributions:
                company['diff'] = 100 * (company.get('contributions', 0) - self.previous_company_contributions[company['company_id']]) / self.previous_company_contributions[company['company_id']]
            yield(company)

    @property
    def members_chart_keys(self):
        activity = self.data['member_activity']
        return activity['days']

    @property
    def members_chart_counts(self):
        activity = self.data['member_activity']
        return activity['joined']

    @property
    def members_chart_active(self):
        activity = self.data['member_activity']
        return activity['active']

    @property
    def members_previous_counts(self):
        if self.previous is None:
            return []
        activity = self.previous_data['member_activity']
        return activity['joined']

    @property
    def members_previous_active(self):
        if self.previous is None:
            return []
        activity = self.previous_data['member_activity']
        return activity['active']

    @property
    def has_support_data(self):
        return 'supporter_roles' in self.data

    @property
    def top_support_contributors(self):
        return self.data['top_support_contributors']

    @property
    def supporters_by_role(self):
        role_counts = self.data['supporter_roles']
        chart = PieChart("supporterRoles", title="Supporters by Role")
        chart.add('Community', role_counts['community'], colors.MEMBER.COMMUNITY)
        chart.add('Staff', role_counts['staff'], colors.MEMBER.STAFF)
        chart.add('Bot', role_counts['bot'], colors.MEMBER.BOT)
        self.charts.add(chart)
        return chart

    @property
    def supported_companies(self):
        chart = PieChart("supportedCompanies", title="Supported Companies")
        for company in self.data['supported_companies']:
            chart.add(company['company_name'], company['count'])
        self.charts.add(chart)
        return chart

    @property
    def supported_members_by_tag(self):
        chart = PieChart("supportedMemberTags", title="Supported Members by Tag")
        for tag in self.data['supported_by_member_tag']:
            chart.add(tag['tag_name'], tag['count'], tag['tag_color'])
        self.charts.add(chart)
        return chart

    @login_required
    def as_view(request, community_id, report):
        view = GrowthReport(request, community_id, report)
        if request.method == "POST":
            pass
        return render(request, "savannahv2/report_growth.html", view.context)

    @login_required
    def publish(request, community_id, report):
        if 'cancel' in request.GET:
            return redirect('reports', community_id=community_id)
            
        # conversations.publish_view(request, PublicDashboard.CONVERSATIONS, 'public_conversations')
        # def publish_view(self, request, page, view_name, show_members=False, show_companies=False, pin_time=None):

        view = AnnualReport(request, community_id, report)
        default_name = report.title
        dashboard = PublicDashboard(
            community=report.community,
            page=PublicDashboard.REPORT, 
            created_by=request.user, 
            display_name=default_name, 
            show_members=False,
            show_companies=True,
            pin_time=False,
            filters={'report_id': report.id, 'start': view.start, 'end': view.end}
        )
        if request.method == "POST":
            form = PublicReportForm(instance=dashboard, data=request.POST)
            if form.is_valid():
                new_pub = form.save()
                messages.success(request, "Your shared report is ready! You can share <a href=\"%s\">this link</a> publicly for anyone to view it." % new_pub.get_absolute_url())
                return redirect('public_report', dashboard_id=new_pub.id)
            else:
                messages.error(request, "Unable to create shared report.")

        else:
            form = PublicReportForm(instance=dashboard)

        context = dashboard.apply(view)
        context.update({
            'form': form,
            'filters': {},
        })
        return render(request, 'savannahv2/publish_report.html', context)

    def public(request, community_id, report, dashboard):
        view = GrowthReport(request, community_id, report)
        if not request.user.is_authenticated:
            dashboard.count()
        context = view.context
        context['dashboard'] = dashboard
        context['back_link'] = reverse('report_view', kwargs={'community_id': community_id, 'report_id':report.id})
        return render(request, 'savannahv2/public/report_growth.html', context)

class AnnualReport(SavannahView):
    def __init__(self, request, community_id, report):
        super().__init__(request, community_id)
        self.active_tab = "reports"
        self.report = report
        self.data = json.loads(self.report.data)
        self.charts = set()
        self.previous_company_activity = dict()
        self.previous_company_contributions = dict()
        try:
            self.previous = Report.objects.filter(community=self.report.community, report_type=Report.ANNUAL, generated__lt=report.generated).order_by('-generated')[0]
            self.previous_data = json.loads(self.previous.data)
            if 'top_company_activity' in self.previous_data:
                for company in self.previous_data['top_company_activity']:
                    self.previous_company_activity[company['company_id']] = company['conversations']
            if 'top_company_contributions' in self.previous_data:
                for company in self.previous_data['top_company_contributions']:
                    self.previous_company_contributions[company['company_id']] = company['contributions']
        except:
            self.previous = None
            self.previous_data = None

    @property
    def start(self):
        return self.data['start']
        
    @property
    def end(self):
        return self.data['end']
        
    @property
    def has_company_data(self):
        return 'top_company_contributions' in self.data or 'top_company_activity' in self.data

    @property
    def top_company_activity(self):
        for company in self.data.get('top_company_activity', []):
            if company['company_id'] in self.previous_company_activity:
                company['diff'] = 100 * (company.get('conversations', 0) - self.previous_company_activity[company['company_id']]) / self.previous_company_activity[company['company_id']]
            yield(company)

    @property
    def top_company_contributions(self):
        for company in self.data.get('top_company_contributions', []):
            if company['company_id'] in self.previous_company_contributions:
                company['diff'] = 100 * (company.get('contributions', 0) - self.previous_company_contributions[company['company_id']]) / self.previous_company_contributions[company['company_id']]
            yield(company)

    @property
    def year_name(self):
        return self.data['start'].year
        
    @property
    def new_member_count(self):
        return self.data['counts']['new_members']

    @property
    def new_contributor_count(self):
        return self.data['counts']['new_contributors']

    @property
    def new_company_count(self):
        return self.data['counts'].get('new_companies', 0)

    @property
    def conversation_count(self):
        return self.data['counts']['conversations']

    @property
    def contribution_count(self):
        return self.data['counts']['contributions']

    @property
    def connections_count(self):
        return self.data['counts'].get('connections', 0)

    @property
    def events_count(self):
        return self.data['counts'].get('events', 0)

    @property
    def gifts_count(self):
        return self.data['counts'].get('gifts', 0)

    @property
    def top_contributors(self):
        for member in self.data['top_contributors']:
            yield(member)

    @property
    def top_supporters(self):
        for member in self.data['top_supporters']:
            yield(member)

    @property
    def members_chart_keys(self):
        activity = self.data['member_activity']
        return activity['months']

    @property
    def members_chart_joined(self):
        activity = self.data['member_activity']
        return activity['joined']

    @property
    def members_chart_active(self):
        activity = self.data['member_activity']
        return activity['active']

    @property
    def conversation_sources_chart(self):
        chart = PieChart("conversationSources", title="Conversations by Source")
        for source in self.data['conversation_sources']:
                chart.add(ConnectionManager.display_name(source['connector']), source['conversation_count'])
        self.charts.add(chart)
        return chart

    @property
    def contribution_types_chart(self):
        chart = PieChart("conversationSources", title="Contributions by Type")
        for t in self.data['contribution_types']:
                chart.add("%s in %s" % (t['name'], t['source_name']), t['contribution_count'])
        self.charts.add(chart)
        return chart

    @property
    def contribution_types(self):
        return self.data['contribution_types']

    @login_required
    def as_view(request, community_id, report):
        view = AnnualReport(request, community_id, report)
        if request.method == "POST":
            pass
        return render(request, "savannahv2/report_annual.html", view.context)

    @login_required
    def publish(request, community_id, report):
        if 'cancel' in request.GET:
            return redirect('reports', community_id=community_id)
            
        # conversations.publish_view(request, PublicDashboard.CONVERSATIONS, 'public_conversations')
        # def publish_view(self, request, page, view_name, show_members=False, show_companies=False, pin_time=None):

        view = AnnualReport(request, community_id, report)
        default_name = report.title
        dashboard = PublicDashboard(
            community=report.community,
            page=PublicDashboard.REPORT, 
            created_by=request.user, 
            display_name=default_name, 
            show_members=False,
            show_companies=True,
            pin_time=False,
            filters={'report_id': report.id, 'start': view.start, 'end': view.end}
        )
        if request.method == "POST":
            form = PublicReportForm(instance=dashboard, data=request.POST)
            if form.is_valid():
                new_pub = form.save()
                messages.success(request, "Your shared report is ready! You can share <a href=\"%s\">this link</a> publicly for anyone to view it." % new_pub.get_absolute_url())
                return redirect('public_report', dashboard_id=new_pub.id)
            else:
                messages.error(request, "Unable to create shared report.")

        else:
            form = PublicReportForm(instance=dashboard)

        context = dashboard.apply(view)
        context.update({
            'form': form,
            'filters': {},
        })
        return render(request, 'savannahv2/publish_report.html', context)

    def public(request, community_id, report, dashboard):
        view = AnnualReport(request, community_id, report)
        if not request.user.is_authenticated:
            dashboard.count()
        context = view.context
        context['dashboard'] = dashboard
        context['back_link'] = reverse('report_view', kwargs={'community_id': community_id, 'report_id':report.id})
        return render(request, 'savannahv2/public/report_annual.html', context)