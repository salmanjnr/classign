from __future__ import print_function
import requests
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from abc import ABC, abstractmethod
from base import LMS , Course



class GoogleClassroom(LMS):

    def __init__(self):
        pass
    def authenticate(self):
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


    def list_courses(self):
        '''
        This method retruns the list of courses from GoogleClassroom API
        '''
        x = self.authenticate()
        # Requesting courses from GoogleClasroom API after authenticating
        results = x.courses().list().execute()
        courses = results.get('courses' , [])

        #initialize an empty list to store coures names in it
        courses_list = []
        #Looping to store all course names

        if not courses:
            print('No Courses found')
        else:
            for course in courses:
                courses_list.append(self.__make_course_object(course))

        return  courses_list


    def bulk_download(self):
        # TODO
        pass

    def get_assignments(self):
        pass
    def __make_course_object(self, course_dict):
        course_id = str(course_dict['id'])
        name = course_dict['name']
        return GoogleClasroomCourse(course_id, name)
class GoogleClasroomCourse(Course , GoogleClassroom):
    def __init__(self, course_id, name):
        self.id = course_id
        self.name = name
    def get_assignments(self):
        x = self.authenticate()
        # Requesting courses from GoogleClasroom API after authenticating
        work_results = x.courses().courseWork().list(
        courseId=self.id).execute()
        work = work_results.get("courseWork" , [] )
        assignments = []
        for assignment in work:
            assignments.append(self.__make_simple_assignment_object(assignment))

        return assignments

    def bulk_download(self):
        # TODO
        pass
    def __make_simple_assignment_object(self, assignment_dict):
        assignment_id = str(assignment_dict['id'])
        name = assignment_dict['title']
        due = assignment_dict['dueDate']
        due_date = str(due['day']) + '/' + str(due['month'])
        return SimpleGoogleClassroomAssignment(assignment_id, self.id, name, due_date)

    def __str__(self):
        return "course_id={}\ncourse_name={}\n".format(self.id,self.name )
class SimpleGoogleClassroomAssignment(GoogleClassroom):
    def __init__(self, assignment_id, course_id, name, due_date):
        self.id = assignment_id
        self.course_id = course_id
        self.name = name
        self.due_date = due_date
    def __get_full_course_data(self):
        x = self.authenticate()
        # Requesting courses from GoogleClasroom API after authenticating
        results = x.courses().courseWork().studentSubmissions(
        ).list(courseId =self.course_id , courseWorkId = self.id).execute()
        submissions = results.get('studentSubmissions' , [])
        return submissions
    def make_classroom_assignment_object(self):
        submissions = self.__get_full_course_data()
        state = (submissions[0])['state']
        submission_type = (submissions[0])['courseWorkType']
        submission_id = (submissions[0])['id']
        assignment_object = GoogleClassroomAssignment(self.id, self.course_id,
                            self.name, submission_type, self.due_date, state , submission_id)
        #assignment_object.add_submission_type(submission_type)
        return assignment_object
        def __str__(self):
            return ("assignment_id={}\nassignment_name={}\ndue_date={}").format(self.id,
                                                                    -    self.name,
                                                                        self.due_date)



class GoogleClassroomAssignment(GoogleClassroom):
    def __init__(self, assignment_id, course_id, name, description, due_date,
                 state , submission_id):
        self.id = assignment_id
        self.course_id = course_id
        self.name = name
        self.description = description
        self.due_date = due_date
        self.state = state
        self.submission_id = submission_id


    def __str__(self):
        return ("assignment_id={}\nassignment_name={}\n"
                "assignment_description={}\ndue_date={}").format(self.id, self.name,
                                                                 self.description, self.due_date)
    def add_submission_type(self, submission_type):
        if submission_type == 'SHORT_ANSWER_QUESTION':
            self.online_text_submission = TextEntrySubmission(self.course_id,
                                                    self.id, self.submission_id)
        elif submission_type == 'ASSIGNMENT':
            self.online_upload_submission = FileSubmission(self.course_id,self.id,
                                                           self.submission_id)
        elif  submission_type == 'MULTIPLE_CHOICE_QUESTION':
            self.mcq_submission = MultipleChoiceSubmission(self.course_id,
                                                    self.id, self.submission_id)
        else:
            pass

#class GoogleClassroomSubmission(ABC):
#    def __init__(self,course_id ,  assignment_id, submission_id ):
#        self.course_id = course_id
#        self.assignment_id = assignment_id
#        self.submission_id = submission_id
#
#
#    @abstractmethod
#    def submit(self, *args, **kwargs):
#        pass
#
#    def Turn_in(self):
#        x = self.authenticate()
#        turning_in = x.courses().courseWork().studentSubmissions().turnIn(
#        courseId= self.course_id , courseWorkId =self.assignment_id ,
#        id =self.submission_id
#        ).execute()
#class TextEntrySubmission(GoogleClassroomSubmission , GoogleClassroom):
#    def submit(self , answer):
#        x = self.authenticate()
#        # Requesting courses from GoogleClasroom API after authenticating
#        submission = x.courses().courseWork().studentSubmissions().get(
#        courseId= self.course_id , courseWorkId =self.assignment_id ,
#        id =self.submission_id).execute()
#        #studentSubmission = submission.get('studentSubmissions' , [])
#        (submission["shortAnswerSubmission"])['answer'] = answer
#        #request = x.courses().courseWork().studentSubmissions(
#        #).patch(courseId= self.course_id , courseWorkId =self.assignment_id ,
#        #id =self.submission_id ,
#        # updateMask =  "shortAnswerSubmission" ,body=submission  ).execute()
#
#        return submission
#class MultipleChoiceSubmission(GoogleClassroomSubmission , GoogleClassroom):
#    def submit(self,answer):
#        x = self.authenticate()
#        # Requesting courses from GoogleClasroom API after authenticating
#        submission = x.courses().courseWork().studentSubmissions().get(
#        courseId= self.course_id , courseWorkId =self.assignment_id ,
#        id =self.submission_id).execute()
#        studentSubmission = submission.get('studentSubmissions' , [])
#        studentSubmission['MULTIPLE_CHOICE_QUESTION'] = answer
#        request = x.courses().courseWork().studentSubmissions(
#        ).patch(courseId= self.course_id , courseWorkId =self.assignment_id ,
#        id =self.submission_id ,
#        body=studentSubmission , updateMask =  'MULTIPLE_CHOICE_QUESTION' ).execute()
#        return request

#class FileSubmission(GoogleClassroomSubmission):
#    def submit_url(self , url):
#        x = self.authenticate()
#        # Requesting courses from GoogleClasroom API after authenticating
#        submission = x.courses().courseWork().studentSubmissions().modifyAttachments(
#        id =self.submission_id, body = ("addAttachments" = ["alternateLink" =  url])).excute()
#        studentSubmission = submission.get('studentSubmissions' , [])
#
#        return studentSubmission
