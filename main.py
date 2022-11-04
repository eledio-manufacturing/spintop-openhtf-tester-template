from pprint import pprint
from time import sleep
import re

from openhtf.plugs.user_input import UserInput
from spintop_openhtf import TestPlan
from openhtf import PhaseResult
from openhtf.util import conf, format_string, data
from openhtf.output.callbacks import json_factory
from openhtf.core.test_record import PhaseOutcome


conf.declare('label_printer', default_value='eledio', description='Label printer')


FORM_LAYOUT = {
    'schema': {
        'title': "Select DUT ID",
        'type': "object",
        'properties': {
            'dutID': {
                'type': "string",
                'title': "DUT ID - for repeated test only",
                "placeholder": "AAA-BBB-CCC"
            }
        }
    },
    'layout': [
        "dutID"
    ]
}

""" Test Plan """

# This defines the name of the testbench.
plan = TestPlan('EVCC')


@plan.trigger('Configuration of test (select DUT ID)')
@plan.plug(prompts=UserInput)
def trigger(test, prompts):
    """Display the configuration form"""
    response = prompts.prompt_form(FORM_LAYOUT)
    pprint(response)
    test.dut_id = response['dutID']


if __name__ == '__main__':
    with open('station_config/config.yaml') as f:
        conf.load_from_file(f)
    plan.run(launch_browser=False)