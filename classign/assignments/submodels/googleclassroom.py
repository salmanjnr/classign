from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from urllib.parse import urljoin
import requests
from django.db import models

from datetime import datetime
import pytz
from abc import abstractmethod



class GoogleClassroom(models.Model):
    """
    Represents a GoogleClassroom account.
    """

    def __authenticate(self):
        '''
        This method is used to authenticate using Oauth 2.0 and using Gmail
        account linked to Classroom
        '''
        SCOPES = ['https://www.googleapis.com/auth/classroom.student-submissions.me.readonly' ,
           'https://www.googleapis.com/auth/classroom.courses.readonly' ,
           'https://www.googleapis.com/auth/classroom.coursework.me' ,
            'https://www.googleapis.com/auth/classroom.coursework.students'
        ]
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

    def update_courses(self):
        """
        This Method updates the courses from the Classroom API
        """
        x = self.__authenticate()
        # Requesting courses from GoogleClasroom API after authenticating
        results = x.courses().list().execute()
        courses = results.get('courses' , [])
        # Looping over courses to create course objects
        for course in courses:
            course_id = str(course['id'])
            course_name = course['name']
            try:
                # if course is already there, update info
                course = self.googleclassroomcourse_set.get(course_id=course_id)
                course.name = course_name
                course.save()
            except GoogleClassroomCourse.DoesNotExist:
                # if course not registered in database, register it.
                GoogleClassroomCourse.objects.create(lms=self, course_id=course_id, name=course_name)
        return courses

    def get_todo(self):
        """
        Get GoogleClassroom TODO.
        """
        # initilaize GMT time zone to check the deadline (API clock is GMT)
        tz = pytz.timezone("GMT")
        # update the courses to get all the new assignments
        y = self.update_courses()
        self.googleclassroomassignment_set.all().delete()
        x = self.__authenticate()
        assignments = []
        for coursee in y :
            #we loop over courses to get courseWork
            work_results = x.courses().courseWork().list(courseId=coursee['id']).execute()
            coursework = work_results.get("courseWork" , [] )
            for assignment in coursework:
                # Creating objects for the courses
                course = self.googleclassroomcourse_set.get(course_id=coursee['id'])
                assignment_id = str(assignment['id'])
                assignment_name = assignment['title']
                assignment_description = assignment['workType']
                course_id = assignment['courseId']
            try:
                #WE Check the Due date becasue if there is no date it returns Key Error
                due = assignment['dueDate']
                time = assignment['dueTime']
                # We extract the due date from the courseWork
                due_date = datetime(int(due['year']) , int(due['month'])
                , int(due['day']) , int(time["hours"]), int(time["minutes"]), 00)
                now = datetime.now(tz)
                due_date = tz.localize(due_date)
                #comparing due date to current time
                if now >= due_date:
                    assignment_object = GoogleClassroomAssignment.objects.create(
                        lms=self, course=course,
                        assignment_id=assignment_id,
                        name=assignment_name,
                        due_date=due_date,
                        description=assignment_description)
            except KeyError:
                due_date = None
                assignment_object = GoogleClassroomAssignment.objects.create(
                    lms=self, course=course,
                    assignment_id=assignment_id,
                    name=assignment_name,
                    due_date=due_date,
                    description=assignment_description)

        return self.googleclasroomassignment_set.all()

class GoogleClassroomCourse(models.Model):
    """
    Represents a GoogleClassroom course.
    Parameters:
        lms (GoogleClassroom) : the GoogleClassroomaccount associated with the course.
        course_id (str): the id of the course on GoogleClassroom.
        name (str): the course name on GoogleClassroom.

    """
    lms = models.ForeignKey(to=GoogleClassroom, on_delete=models.CASCADE)
    course_id = models.CharField(max_length=100)
    name = models.CharField(max_length=200)

class GoogleClassroomAssignment(models.Model):
    """
    Represents a GoogleClassroom assignment.
    Parameters:
        lms (GoogleClassroom): the GoogleClassroom account associated with the assignment.
        course (GoogleClassroomCourse): the GoogleClassroom course associated with the assignment.
        assignment_id (str): the id of the assignment on GoogleClassroom.
        name (str): the name of the assignment.
        due_date (datetime objects): the deadline of the assignment.
        description (str): the description of the assignment.
    """
    lms = models.ForeignKey(to=GoogleClassroom, on_delete=models.CASCADE, null=True)
    course = models.ForeignKey(to=GoogleClassroomCourse, on_delete=models.CASCADE, null=True)
    assignment_id = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    due_date = models.DateTimeField('due date', null=True)
    description = models.TextField()
