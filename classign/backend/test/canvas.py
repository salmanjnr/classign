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
        self.assertEqual(courses[0].id, 1841767)

    def test_get_assignemnts(self):
        assignments = self.canvas.get_assignments()
        self.assertEqual(len(assignments), 10)


unittest.main()
