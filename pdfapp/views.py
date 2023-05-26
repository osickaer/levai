from .utils import parse_pdf, extract_fields_from_pdf
from django.contrib import messages
from django import forms
from django.shortcuts import render, redirect
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle
import pandas as pd
from datetime import timedelta
from django.contrib.auth.decorators import login_required

SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_google():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                './credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def get_calendars(service):
    calendar_list = service.calendarList().list().execute()
    calendars = [(cal['id'], cal['summary']) for cal in calendar_list['items']]
    return calendars

# Form for uploading a PDF file and selecting a calendar
class UploadFileForm(forms.Form):
    file = forms.FileField()
    calendar_id = forms.ChoiceField(choices=[])  # initialize with an empty list

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(UploadFileForm, self).__init__(*args, **kwargs)
        if user:
            credentials = authenticate_google()
            service = build('calendar', 'v3', credentials=credentials)
            self.fields['calendar_id'].choices = get_calendars(service)


def create_event(service, summary, event_date, calendar_id):
    # ... your existing code ...
    # Replace the hard-coded calendarId with the one provided by the user
    event = {
        'summary': summary,
        'start': {
            'date': event_date.strftime('%Y-%m-%d'),
            'timeZone': 'America/Denver',  # Replace with your desired time zone
        },
        'end': {
            'date': (event_date + timedelta(days=1)).strftime('%Y-%m-%d'),
            'timeZone': 'America/Denver',  # Replace with your desired time zone
        },
        'reminders': {
            'useDefault': False,
        },
    }
    event = service.events().insert(calendarId=calendar_id, body=event).execute()

def upload_file(request):
    # if not request.user.is_authenticated:
    #     messages.error(request, 'Please log in before you continue.')
    #     return redirect('home')
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            # Call the function to authenticate and authorize
            credentials = authenticate_google()

            # Create the Google Calendar service
            service = build('calendar', 'v3', credentials=credentials)

            # Parse the PDF file
            df = parse_pdf(request.FILES['file'])

            # Extract the events and add them to the calendar
            for index, row in df.iterrows():
                event = row["Event"]
                deadline = row["Date or Deadline"]
                event_date = pd.to_datetime(deadline).date()
                create_event(service, event, event_date, form.cleaned_data['calendar_id'])

            return render(request, 'success.html')
    else:
        form = UploadFileForm(user=request.user)
    return render(request, 'upload.html', {'form': form})

def google_login(request):
    credentials = authenticate_google()
    return redirect('home')

def home(request):
    return render(request, 'home.html')
