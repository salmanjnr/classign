import requests
from abc import ABC, abstractmethod
from classign.backend.services.base import LMS, Course


def canvasmethod(function):
    # only wrap regular functions
    def wrapped_function(*args, **kwargs):
        assert len(args) != 0
        instance = args[0]
        assert isinstance(instance, Canvas)
        Canvas.refresh_authentication(instance)
        result = function(*args, **kwargs)
        return result
    return wrapped_function


class Canvas(LMS):
    def __init__(self):
        self.access_token = self.authenticate()

    def authenticate(self):
        # TODO
        pass

    def refresh_authentication(self):
        # TODO
        pass

    @canvasmethod
    def list_courses(self):
        list_courses_request = ("https://canvas.instructure.com/api/v1/courses?access_token={}&"
                                "enrollment_type=student")
        response = requests.get(list_courses_request.format(self.access_token)).json()

        courses = list()
        for course in response:
            courses.append(self.__make_course_object(course))

        return courses

    @canvasmethod
    def get_assignments(self):
        courses = self.list_courses()
        assignments = list()
        for course in courses:
            assignments += course.get_assignments()
        return assignments

    @canvasmethod
    def bulk_download(self):
        # TODO
        pass

    def __make_course_object(self, course_dict):
        course_id = str(course_dict['id'])
        name = course_dict['name']
        course_code = course_dict['course_code']
        return CanvasCourse(course_id, name, course_code, self.access_token)


class CanvasCourse(Course):
    def __init__(self, course_id, name, course_code, student_access_token):
        self.id = course_id
        self.name = name
        self.course_code = course_code
        self.student_access_token = student_access_token

    def get_assignments(self):
        get_assignments_request = ("https://canvas.instructure.com/api/v1/courses/{}/"
                                   "assignments?access_token={}")
        response = requests.get(get_assignments_request.format(self.id,
                                                               self.student_access_token)).json()

        assignments = list()
        for assignment in response:
            assignments.append(self.__make_simple_assignment_object(assignment))

        return assignments

    def bulk_download(self):
        # TODO
        pass

    def __make_simple_assignment_object(self, assignment_dict):
        assignment_id = str(assignment_dict['id'])
        name = assignment_dict['name']
        due_date = assignment_dict['due_at']
        return SimpleCanvasAssignment(assignment_id, self.id, name, due_date,
                                      self.student_access_token)

    def __str__(self):
        return "course_id={}\ncourse_name={}\ncourse_code={}\n".format(self.id,
                                                                       self.name,
                                                                       self.course_code)


class SimpleCanvasAssignment:
    def __init__(self, assignment_id, course_id, name, due_date, student_access_token):
        self.id = assignment_id
        self.course_id = course_id
        self.name = name
        self.due_date = due_date
        self.student_access_token = student_access_token

    def __get_full_course_data(self):
        get_assignments_request = ("https://canvas.instructure.com/api/v1/courses/{}/"
                                   "assignments/{}?access_token={}&include[]=can_submit")
        response = requests.get(get_assignments_request.format(self.course_id,
                                                               self.id,
                                                               self.student_access_token)).json()
        return response

    def make_canvas_assignment_object(self):
        response = self.__get_full_course_data()
        can_submit = response["can_submit"]
        description = response["description"]
        assignment_object = CanvasAssignment(self.id, self.course_id, self.name, description,
                                             self.due_date, can_submit, self.student_access_token)
        submission_types = response["submission_types"]
        for submission_type in submission_types:
            assignment_object.add_submission_type(submission_type)
        return assignment_object

    def __str__(self):
        return ("assignment_id={}\nassignment_name={}\ndue_date={}").format(self.id,
                                                                            self.name,
                                                                            self.due_date)


class CanvasAssignment:
    def __init__(self, assignment_id, course_id, name, description, due_date, can_submit,
                 student_access_token):
        self.id = assignment_id
        self.course_id = course_id
        self.name = name
        self.description = description
        self.due_date = due_date
        self.can_submit = can_submit
        self.student_access_token = student_access_token

    def __str__(self):
        return ("assignment_id={}\nassignment_name={}\n"
                "assignment_description={}\ndue_date={}").format(self.id, self.name,
                                                                 self.description, self.due_date)

    def add_submission_type(self, submission_type):
        if submission_type == 'online_text_entry':
            self.online_text_submission = TextEntrySubmission(self.id, self.course_id,
                                                              self.student_access_token)
        elif submission_type == 'online_upload':
            self.online_upload_submission = FileSubmission(self.id, self.course_id,
                                                           self.student_access_token)
        else:
            pass


class CanvasSubmission(ABC):
    def __init__(self, assignment_id, course_id, student_access_token):
        self.assignment_id = assignment_id
        self.course_id = course_id
        self.student_access_token = student_access_token

    @abstractmethod
    def submit(self, *args, **kwargs):
        pass


class TextEntrySubmission(CanvasSubmission):
    def submit(self, body, comment=None):
        submission_request = ('https://canvas.instructure.com/api/v1/courses/'
                              '{}/assignments/{}/submissions?access_token={}')

        json = {'submission': {'submission_type': 'online_text_entry',
                               'body': body}}
        if comment is not None:
            json['comment'] = {'text_comment': comment}
        requests.post(submission_request.format(self.course_id, self.assignment_id,
                                                self.student_access_token), json=json)


class FileSubmission(CanvasSubmission):
    def __submit_from_url(self, url_list, comment):
        submission_request = ('https://canvas.instructure.com/api/v1/courses/'
                              '{}/assignments/{}/submissions?access_token={}')
        id_list = list()
        name = f'{self.course_id}_{self.assignment_id}_'+'{}'
        for ind, url in enumerate(url_list):
            id_list.append(self.__upload_file_from_url(url, name.format(ind)))

        json = {'submission': {'submission_type': 'online_upload',
                               'file_ids': id_list}}
        if comment is not None:
            json['comment'] = {'text_comment': comment}
        response = requests.post(submission_request.format(self.course_id, self.assignment_id,
                                                           self.student_access_token), json=json)

    def __upload_file_from_url(self, url, name):
        upload_request = ('https://canvas.instructure.com/api/v1/users/self/files?access_token={}')
        json = {'url': url, 'name': name, 'parent_folder_path': f'/CLASSIGN/{self.course_id}'}
        response = requests.post(upload_request.format(self.student_access_token), json=json).json()
        upload_url = response['upload_url']
        upload_params = response['upload_params']
        response = requests.post(upload_url, upload_params).json()
        print(response['id'])
        return response['id']

    def __submit_file(self, files_dict, comment):
        # TODO
        pass

    def submit(self, upload_type='url', url_list=None, files_dict=None, comment=None):
        if upload_type == 'url':
            self.__submit_from_url(url_list, comment)
        else:
            self.__submit_file(files_dict, comment)


class RequestTimeout(Exception):
    pass
