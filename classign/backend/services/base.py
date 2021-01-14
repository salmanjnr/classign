from abc import ABC, abstractmethod


class LMS(ABC):
    @abstractmethod
    def list_courses(self):
        pass

    @abstractmethod
    def get_assignments(self):
        pass

    @abstractmethod
    def bulk_download(self):
        pass


class Course(ABC):
    @abstractmethod
    def get_assignments(self):
        pass

    @abstractmethod
    def bulk_download(self):
        pass
