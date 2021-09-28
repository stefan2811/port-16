from enum import Enum


class AppStatus(Enum):
    STARTED = 'STARTED'
    EXITING = 'EXITING'


class ApplicationStatusService:
    service = None

    def __init__(self):
        self.status = AppStatus.STARTED

    @classmethod
    def instance(cls):
        """
        Creates service instance if not created and returns it.

        :return: Created service instance.
        :rtype: ApplicationStatusService
        """
        if cls.service is None:
            cls.service = ApplicationStatusService()

        return cls.service

    def get_status(self):
        """
        Returns current app status.

        :return: Current stored app status.
        :rtype: AppStatus
        """
        return self.service

    def set_status(self, status: AppStatus = AppStatus.EXITING):
        """
        Sets current app status.

        :param status: current status which is about to be set.
        :return:
        """
        self.status = status
