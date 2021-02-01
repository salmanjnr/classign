from django.test import TestCase
from assignments.models import Canvas
from assignments.models import GoogleClassroom
from os import getenv
from dotenv import load_dotenv


#class TestCanvas(TestCase):
#    def setUp(self):
#        load_dotenv()
#        access_token = getenv('CANVAS_TOKEN')
#        Canvas.objects.create(access_token=access_token)
#
#    def test_update_courses(self):
#        c = Canvas.objects.first()
#        c.update_courses()
#        print(c.canvascourse_set.all())
#
#    def test_get_assignments(self):
#        c = Canvas.objects.first()
#        print(c.get_assignments())
#
#    def test_full_assignment(self):
#        c = Canvas.objects.first()
#        c.update_assignments()
#        c.get_assignments()
#        a = c.simplecanvasassignment_set.first()
#        print(c.get_full_assignment(a))
class TestClassroom(TestCase):
    def setUp(self):
        load_dotenv()
        GoogleClassroom.objects.create()
    def test_update_courses(self):
        g = GoogleClassroom.objects.first()
        g.update_courses()
        print(g.googleclasroomcourse_set.all())
    def test_get_assignments(self):
        g = GoogleClassroom.objects.first()
        print(g.get_todo())
