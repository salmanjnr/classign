from django.db import models
from abc import abstractmethod


class LMS(models.Model):
    class Meta:
        abstract = True

    @abstractmethod
    def get_todo(*args, **kwargs):
        pass

    @abstractmethod
    def update_courses(*args, **kwargs):
        pass


class Course(models.Model):
    class Meta:
        abstract = True


class Assignment(models.Model):
    class Meta:
        abstract = True
