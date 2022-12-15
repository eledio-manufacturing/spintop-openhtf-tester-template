from pprint import pprint
from time import sleep
import re

from openhtf.plugs.user_input import UserInput
from spintop_openhtf import TestPlan
from openhtf import PhaseResult
from openhtf.util import conf, format_string, data
from openhtf.output.callbacks import json_factory
from openhtf.core.test_record import PhaseOutcome

LOG_FILENAME_PATTERN = 'cache/test_results/{dut_id}_{start_time_millis}.test.json'

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
plan = TestPlan('Test')


@plan.trigger('Configuration of test (select DUT ID)')
@plan.plug(prompts=UserInput)
def trigger(test, prompts):
    """Display the configuration form"""
    response = prompts.prompt_form(FORM_LAYOUT)
    pprint(response)
    test.dut_id = response['dutID']


class UploadTestResult(json_factory.OutputToJSON):
    def __init__(self, folder_pattern, indent=4):
        self.folder_pattern = folder_pattern
        super().__init__(indent=indent)

    def __call__(self, test_record):
        if test_record.is_started():
            record_dict = data.convert_to_base_types(
                test_record, ignore_keys=('code_info', 'phases', 'log_records'))

            output_folder = format_string(self.folder_pattern, record_dict)

            _record = self.serialize_test_record(test_record)
            with open(output_folder, 'w') as f:
                f.write(_record)

            # Upload test results here to the ERP
            """
            import json
            from test_tools.tester_core.plugs.erp import ErpPlug
            
            erp = ErpPlug()
            erp.graphql('test_tools/tester_core/graphql/upload_device_files.graphql', files=[output_folder],
                        sn=json.loads(_record)["dut_id"])
            if record_dict['outcome'] == 'PASS':
                erp.graphql('test_tools/tester_core/graphql/set_device_state.graphql', state='ok',
                            sn=json.loads(_record)["dut_id"])
            else:
                erp.graphql('test_tools/tester_core/graphql/set_device_state.graphql', state='defective',
                            sn=json.loads(_record)["dut_id"])
            """


if __name__ == '__main__':
    with open('station_config/config.yaml') as f:
        conf.load_from_file(f)
    plan.add_callbacks(UploadTestResult(LOG_FILENAME_PATTERN, indent=2))
    plan.run(launch_browser=False)