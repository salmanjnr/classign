import requests
from classign.backend.services.base import LMS, Course, Assignment


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
        pass

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
        course_id = course_dict['id']
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
        get_assignments_request = ("https://canvas.instructure.com/api/v1/courses/1841767/"
                                   "assignments?access_token={}")
        response = requests.get(get_assignments_request.format(self.student_access_token)).json()

        assignments = list()
        for assignment in response:
            assignments.append(self.__make_assignment_object(assignment))

        return assignments

    def bulk_download(self):
        # TODO
        pass

    def __make_assignment_object(self, assignment_dict):
        assignment_id = assignment_dict['id']
        name = assignment_dict['name']
        description = assignment_dict['description']
        due_date = assignment_dict['due_at']
        return CanvasAssignment(assignment_id, name, description, due_date,
                                self.student_access_token)

    def __str__(self):
        return "course_id={}\ncourse_name={}\ncourse_code={}\n".format(self.id,
                                                                       self.name,
                                                                       self.course_code)


class CanvasAssignment(Assignment):
    def __init__(self, assignment_id, name, description, due_date, student_access_token):
        self.id = assignment_id
        self.name = name
        self.description = description
        self.due_date = due_date
        self.student_access_token = student_access_token

    def submit(self):
        # TODO
        pass

    def unsubmit(self):
        # TODO
        pass

    def __str__(self):
        return ("assignment_id={}\nassignment_name={}\n"
                "assignment_description={}\ndue_date={}").format(self.id, self.name,
                                                                 self.description, self.due_date)
