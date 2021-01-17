import unittest
from dotenv import load_dotenv
from os import getenv
from classign.backend.services.canvas import Canvas


class CanvasForTest(Canvas):
    def authenticate(self):
        load_dotenv()
        return getenv('CANVAS_TOKEN')


class TestCanvas(unittest.TestCase):
    def setUp(self):
        self.canvas = CanvasForTest()

    def test_list_assignments(self):
        courses = self.canvas.list_courses()
        self.assertEqual(courses[0].id, '1841767')

    def test_get_assignemnts(self):
        assignments = self.canvas.get_assignments()
        print(assignments[0])
        self.assertTrue(len(assignments) != 0)

    def test_complex_assignments(self):
        simple_assignmnents = self.canvas.get_assignments()
        assignment_1 = simple_assignmnents[0]
        complex_assignment_1 = assignment_1.make_canvas_assignment_object()
        print(complex_assignment_1)

    def test_file_upload_submission(self):
        simple_assignmnents = self.canvas.get_assignments()
        sample_assignment = None
        for assignment in simple_assignmnents:
            if assignment.id == '19728737':
                sample_assignment = assignment
        sample_assignment = sample_assignment.make_canvas_assignment_object()
        sample_assignment.online_text_submission.submit('hi')
        sample_assignment.online_upload_submission.submit(url_list=['https://images.theconversati'
                                                                    'on.com/files/93616/original/'
                                                                    'image-20150902-6700-t2axrz.j'
                                                                    'pg'], comment='hi')


unittest.main()
