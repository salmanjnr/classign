from assignments.submodels.base import LMS, Course, Assignment
from urllib.parse import urljoin
import requests
from django.db import models
from django.utils import timezone
from datetime import datetime
from abc import abstractmethod


class Canvas(LMS):
    """
    Represents a canvas account.

    Parameters:
        access_token (str): canvas api access token.
        school_address (str): the address of the school's canvas profile
    """

    access_token = models.CharField(max_length=100)
    school_address = models.CharField(max_length=100, default='https://canvas.instructure.com')

    def update_courses(self):
        """
        Update courses associated with the acount.
        """
        request_part = '/api/v1/courses?access_token={}&enrollment_type=student'.format(
            self.access_token)
        list_courses_request = urljoin(str(self.school_address), request_part)
        response = requests.get(list_courses_request).json()  # get courses through canvas apis
        for course in response:
            course_id = str(course['id'])
            course_name = course['name']
            course_code = course['course_code']
            try:
                # if course is already there, update info
                course = self.canvascourse_set.get(course_id=course_id)
                course.name = course_name
                course_code = course_code
                course.save()
            except CanvasCourse.DoesNotExist:
                # if course not registered in database, register it.
                CanvasCourse.objects.create(lms=self, course_id=course_id, name=course_name,
                                            course_code=course_code)

    def get_todo(self):
        """
        Get canvas TODO.
        """
        self.update_courses()  # make sure courses are up to date.
        self.canvasassignment_set.all().delete()  # to avoid duplicates.
        request_part = '/api/v1/users/self/todo?access_token={}'.format(self.access_token)
        todo_request = urljoin(str(self.school_address), request_part)
        response = requests.get(todo_request).json()
        for item in response:
            if (item['type'] == 'submitting') and ('assignment' in item):  # only assignments
                # extract attributes
                assignment = item['assignment']
                assignment_id = str(assignment['id'])
                assignment_name = assignment['name']
                assignment_description = assignment['description']
                course_id = assignment['course_id']
                course = self.canvascourse_set.get(course_id=course_id)
                # set due date
                if assignment['due_at'] is None:
                    due_date = None
                else:
                    due_date = datetime.strptime(assignment['due_at'], '%Y-%m-%dT%H:%M:%SZ')
                    due_date = timezone.make_aware(due_date)
                # create objects
                assignment_object = CanvasAssignment.objects.create(
                    lms=self, course=course,
                    assignment_id=assignment_id,
                    name=assignment_name,
                    due_date=due_date,
                    description=assignment_description)

                # create submission objects
                for submission_type in assignment['submission_types']:
                    self.__submission_factory(submission_type, assignment_object)

        return self.canvasassignment_set.all()

    def submit(self, assignment, url=None, text=None, files=None):
        """
        Submit assignment solution.

        Parameters:
            assignment (CanvasAssignment): the assignment associated with the submission
            url (str): the url of the file (if file submission).
            text (str): the html text (if online_text submission).
            files (list): the list of file ids on canvas (if file submission)/
        """
        if (url is not None) + (text is not None) + (files is not None) != 1:
            raise SubmissionException('Exactly one of url, text, and files should be passed')

        if url:
            self.__submit_from_url(assignment, url)

        if files:
            self.__submit_files(assignment, files)

        if text:
            self.__submit_text(assignment, text)

    def __submit_from_url(self, assignment, url):
        # submit assignment from url. this is a helper function
        request_part = '/api/v1/courses/{}/assignments/{}/submissions?access_token={}'.format(
            assignment.course.course_id, assignment.assignment_id, self.access_token)
        submit_request = urljoin(str(self.school_address), request_part)
        course = assignment.course
        name = f'{course.course_id}_{assignment.assignment_id}'
        file_id = self.__upload_from_url(course, url, name)
        json = {'submission': {'submission_type': 'online_upload',
                               'file_ids': [file_id]}}
        requests.post(submit_request, json=json)

    def __upload_from_url(self, course, url, name):
        # upload file to canvas from url. this is a helper function
        request_part = '/api/v1/users/self/files?access_token={}'.format(self.access_token)
        upload_request = urljoin(str(self.school_address), request_part)
        json = {'url': url, 'name': name, 'parent_folder_path': f'/CLASSIGN/{course.course_id}'}
        response = requests.post(upload_request, json=json).json()
        upload_url = response['upload_url']
        upload_params = response['upload_params']
        response = requests.post(upload_url, upload_params).json()
        return response['id']

    def __submit_files(self, assignment, files):
        # TODO
        pass

    def __submit_text(self, assignment, text):
        # submit text to canvas
        request_part = '/api/v1/courses/{}/assignments/{}/submissions?access_token={}'.format(
            assignment.course.course_id, assignment.assignment_id, self.access_token)
        submit_request = urljoin(str(self.school_address), request_part)
        json = {'submission': {'submission_type': 'online_text_entry',
                               'body': text}}
        requests.post(submit_request, json=json)

    def __submission_factory(self, submission, assignment):
        # this function creates the appropriate submission object for each submission type.
        if submission == 'online_text_entry':
            return CanvasTextSubmission.objects.create(lms=self, course=assignment.course,
                                                       assignment=assignment)
        elif submission == 'online_upload':
            return CanvasFileSubmission.objects.create(lms=self, course=assignment.course,
                                                       assignment=assignment)


class CanvasCourse(Course):
    """
    Represents a canvas course.

    Parameters:
        lms (Canvas): the canvas account associated with the course.
        course_id (str): the id of the course on canvas.
        name (str): the course name on canvas.
        course_code (str): the code of the course registered on canvas.
    """
    lms_name = models.CharField(max_length=20, default="canvas")
    lms = models.ForeignKey(to=Canvas, on_delete=models.CASCADE)
    course_id = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    course_code = models.CharField(max_length=10)


class CanvasAssignment(Assignment):
    """
    Represents a canvas assignment.

    Parameters:
        lms (Canvas): the canvas account associated with the assignment.
        course (CanvasCourse): the canvas course associated with the assignment.
        assignment_id (str): the id of the assignment on canvas.
        name (str): the name of the assignment.
        due_date (datetime objects): the deadline of the assignment.
        description (str): the description of the assignment.
    """
    lms_name = models.CharField(max_length=20, default="canvas")
    lms = models.ForeignKey(to=Canvas, on_delete=models.CASCADE, null=True)
    course = models.ForeignKey(to=CanvasCourse, on_delete=models.CASCADE, null=True)
    assignment_id = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    due_date = models.DateTimeField('due date', null=True)
    description = models.TextField()


class CanvasSubmission(models.Model):
    """
    Represents a submission for an assignment. This is an abstract base class.
    """
    lms_name = models.CharField(max_length=20, default="canvas")
    lms = models.ForeignKey(to=Canvas, on_delete=models.CASCADE)
    course = models.ForeignKey(to=CanvasCourse, on_delete=models.CASCADE, null=True)
    assignment = models.ForeignKey(to=CanvasAssignment, on_delete=models.CASCADE, null=True)

    class Meta:
        abstract = True

    @abstractmethod
    def submit(*args, **kwargs):
        pass


class CanvasTextSubmission(CanvasSubmission):
    """
    Represents a canvas text submission.

    Parameters:
        lms (Canvas): the canvas account associated with the submission.
        course (CanvasCourse): the canvas course associated with the submission.
        assignment (CanvasAssignment): the canvas assignment associated with the submission.
    """
    def submit(self, text):
        """
        Submits the text using Canvas.submit method.

        Parameters:
            text (str): the text to be submitted.
        """
        self.lms.submit(self.assignment, text=text)


class CanvasFileSubmission(CanvasSubmission):
    """
    Represents a canvas file submission.

    Parameters:
        lms (Canvas): the canvas account associated with the submission.
        course (CanvasCourse): the canvas course associated with the submission.
        assignment (CanvasAssignment): the canvas assignment associated with the submission.
    """
    def submit(self, url=None, files=None):
        """
        Submits the files using Canvas.submit method.

        Parameters:
            url (str): the url of the file.
            files (list): the ids of the files on canvas files.
        """
        if (url is None) and (files is None) or (url is not None) and (files is not None):
            raise SubmissionException("Exactly one of 'url' and 'files' should be passed.")
        if url:
            self.__submit_from_url(url)
        else:
            self.__submit_files(files)

    def __submit_from_url(self, url):
        self.lms.submit(self.assignment, url=url)

    def __submit_files(self, files):
        self.lms.submit(self.assignment, files=files)


class SubmissionException(Exception):
    pass
