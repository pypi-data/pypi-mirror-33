import logging

from alerta.actions import app
from alerta.actions import ActionBase

LOG = logging.getLogger('alerta.actions.gitlab')


class GitlabIssue(ActionBase):

    def take_action(self, alert, action, text):
        """should return internal id of external system"""
        print('take action to create gitlab issue')
        return

    def update_alert(self, alert):
        return alert
