import logging
import os
import sys

from python_agent.test_listener.executors.test_frameworks.agent_execution import AgentExecution

log = logging.getLogger(__name__)


class PytestAgentExecution(AgentExecution):

    def __init__(self, config_data, labid, test_stage, cov_report, args):
        super(PytestAgentExecution, self).__init__(config_data, labid, test_stage=test_stage, cov_report=cov_report)
        self.args = args

    def execute(self):
        try:
            args = list(self.args)
            from pytest import main as pytest_main
            from python_agent.test_listener.integrations import pytest_helper

            # we're appending the current working directory for customers running pytest using: "python -m pytest"
            # https://github.com/pytest-dev/pytest/blob/beacecf29ba0b99511a4e5ae9b96ff2b0c42c775/doc/en/usage.rst
            sys.path.append(os.getcwd())

            pytest_main(args=args, plugins=[pytest_helper.SealightsPlugin()])
        except ImportError as e:
            log.exception("Failed Importing pytest. Error: %s" % str(e))
