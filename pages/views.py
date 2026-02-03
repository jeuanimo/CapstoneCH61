from django.shortcuts import render
from django.contrib import messages
from django.db.models import Q
from django_filters import CharFilter, FilterSet
from .models import Event
from datetime import datetime, timedelta
import calendar

# Create your views here.

class EventFilter(FilterSet):
    title = CharFilter(field_name='title', lookup_expr='icontains')
    
    class Meta:
        model = Event
        fields = ['title']

def home_view(request):
    """Home page view"""
    # Get upcoming events for the calendar modal
    now = datetime.now()
    upcoming_events = Event.objects.filter(
        start_date__gte=now
    ).order_by('start_date')[:5]  # Limit to next 5 events
    
    context = {
        'upcoming_events': upcoming_events
    }
    
    return render(request, 'pages/home.html', context)

def about(request):
    """About page view"""
    return render(request, 'pages/about.html')

def events(request):
    """Events & Service page view with searchable calendar"""
    events_list = Event.objects.all()
    filterset = EventFilter(request.GET, queryset=events_list)
    events_filtered = filterset.qs
    
    # Get the current month for calendar view
    now = datetime.now()
    year = int(request.GET.get('year', now.year))
    month = int(request.GET.get('month', now.month))
    
    # Generate calendar for the month
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    # Get events for the current month
    events_this_month = Event.objects.filter(
        start_date__year=year,
        start_date__month=month
    ).order_by('start_date')
    
    context = {
        'filterset': filterset,
        'events': events_filtered,
        'calendar': cal,
        'month': month,
        'year': year,
        'month_name': month_name,
        'events_this_month': events_this_month,
    }
    return render(request, 'pages/events.html', context)

def news(request):
    """News page view"""
    return render(request, 'pages/news.html')

def programs(request):
    """Programs page view"""
    return render(request, 'pages/programs.html')

def chapter_history(request):
    """Chapter History page view"""
    return render(request, 'pages/chapter_history.html')

def chapter_leadership(request):
    """Chapter Leadership page view"""
    return render(request, 'pages/chapter_leadership.html')

def chapter_membership(request):
    """Chapter Membership page view"""
    return render(request, 'pages/chapter_membership.html')

def chapter_programs(request):
    """Chapter Programs page view"""
    return render(request, 'pages/chapter_programs.html')

def action(request):
    """Nu Gamma Sigma in Action page view"""
    return render(request, 'pages/action.html')

def signin(request):
    """Sign in page view"""
    return render(request, 'pages/signin.html')

def contact(request):
    """Contact page view"""
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message_text = request.POST.get('message', '').strip()
        
        # Basic validation
        if not all([name, email, subject, message_text]):
            messages.error(request, 'All fields are required.')
            return render(request, 'pages/contact.html')
        
        # TODO: Add email sending functionality here
        messages.success(request, 'Thank you for your message! We will get back to you soon.')
        return render(request, 'pages/contact.html')
    
    return render(request, 'pages/contact.html')
 
