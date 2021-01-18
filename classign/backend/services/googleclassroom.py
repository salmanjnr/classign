from __future__ import print_function
import requests
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from base import LMS , Course



class GoogleClassroom(LMS):

    def __init__(self):
        pass
    def authenticate(self):
        '''
        This method is used to authenticate using Oauth 2.0 and using Gmail
        account linked to Classroom
        '''
        SCOPES = ['https://www.googleapis.com/auth/classroom.courses.readonly',
         'https://www.googleapis.com/auth/classroom.student-submissions.me.readonly']
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
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('classroom', 'v1', credentials=creds)
        return service


    def list_courses(self):
        '''
        This method retruns the list of courses from GoogleClassroom API
        '''
        x = self.authenticate()
        # Requesting courses from GoogleClasroom API after authenticating
        results = x.courses().list().execute()
        courses = results.get('courses' , [])

        #initialize an empty list to store coures names in it
        courses_name = []
        #Looping to store all course names
        assignments = []
        if not courses:
            print('No Courses found')
        else:
            for course in courses:
                courses_name.append(course['name'])
        if not courses:
            print('No Courses found')
        else:
            for course in courses:
                work_results = x.courses().courseWork().list(
                courseId=course['id']).execute()
                work = work_results.get("courseWork" , [] )

                for assignment in  work:
                    assignments.append(assignment['title'])

        return  assignments

    def bulk_download(self):
        # TODO
        pass

    def get_assignments(self):
        pass

x = GoogleClassroom()
print(x.list_courses())
