from urllib.parse import urljoin
import requests
from django.db import models
from django.utils import timezone
from datetime import datetime
import pytz
from abc import abstractmethod



class GoogleClassroom(models.Model):

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
        x = self.__authenticate()
        # Requesting courses from GoogleClasroom API after authenticating
        results = x.courses().list().execute()
        courses = results.get('courses' , [])
        for course in courses:
            course_id = str(course['id'])
            course_name = course['name']
            try:
                course = self.gclassroomcourse_set.get(course_id=course_id)
                course.name = course_name
                course.save()
            except GoogleClasroomCourse.DoesNotExist:
                GoogleClasroomCourse.objects.create(lms=self, course_id=course_id, name=course_name,
                                            )
        return courses
    def get_todo(self):
        tz = pytz.timezone("GMT")
        y = self.update_courses()
        self.gclassroomassignment_set.all().delete()
        x = self.__authenticate()
        assignments = []
        for course in y :
            work_results = x.courses().courseWork().list(courseId=course['id']).execute()
            coursework = work_results.get("courseWork" , [] )
            for assignment in coursework:
                course = self.gclassroomcourse_set.get(course_id=course['id'])
                assignment_id = str(assignment['id'])
                assignment_name = assignment['title']
                assignment_description = assignment['workType']
                course_id = assignment['courseId']
            try:
                due = assignment['dueDate']
                time = assignment['dueTime']
                #due_date = str(due['day']) + '/' + str(due['month']) + " " +
                           #str(time["hours"]) + ':' + str(time["minutes"])
                due_date = datetime.datetime(int(due['year']) , int(due['month'])
                , int(due['day']) , int(time["hours"]), int(time["minutes"]), 00)
                now = datetime.now(tz)
                if now >= due_date:
                    assignment_object = GoogleClasroomAssignment.objects.create(
                        lms=self, course=course,
                        assignment_id=assignment_id,
                        name=assignment_name,
                        due_date=due_date,
                        description=assignment_description)
            except KeyError:
                due_date = None
                assignment_object = GoogleClasroomAssignment.objects.create(
                    lms=self, course=course,
                    assignment_id=assignment_id,
                    name=assignment_name,
                    due_date=due_date,
                    description=assignment_description)

        return self.gclassroomassignment_set.all()

class GoogleClasroomCourse(models.Model):
    lms = models.ForeignKey(to=GoogleClassroom, on_delete=models.CASCADE)
    course_id = models.CharField(max_length=100)
    name = models.CharField(max_length=200)

class CanvasAssignment(models.Model):
    lms = models.ForeignKey(to=GoogleClassroom, on_delete=models.CASCADE, null=True)
    course = models.ForeignKey(to=GoogleClasroomCourse, on_delete=models.CASCADE, null=True)
    assignment_id = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    due_date = models.DateTimeField('due date', null=True)
    description = models.TextField()
