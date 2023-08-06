# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
from past.builtins import long
from builtins import range
from threading import Lock
from threading import Timer
import signal
import requests
import jsonschema
import time
import json
import copy
import hashlib
from random import choice
from string import ascii_lowercase
from string import ascii_uppercase
from string import digits
from datetime import datetime
from dateutil.parser import parse as parse_date
from dateutil import tz

SCHEMA = {
    "type": "object",
    "properties": {
        "type": {
            "type": "string",
            "pattern": "^([A-Z][a-zA-Z]*)+$",
            "maxLength": 50,
        },
        "is_group": {
            "type": "boolean",
        },
        "id": {
            "type": ["string", "integer"],
            "pattern": "^[ -~]+$",
            "maxLength": 250,
            "minLength": 1,
        },
        "display_name": {
            "type": "string",
            "maxLength": 250,
            "minLength": 1,
        },
        "is_anonymous": {
            "type": "boolean",
        },
        "attributes": {
            "type": "object",
            "patternProperties": {
                "^[a-zA-Z][a-zA-Z_]{0,48}[a-zA-Z]$": {
                    "oneOf": [
                        {
                            "type": "string",
                            "maxLength": 3000,
                        },
                        {
                            "type": "boolean"
                        },
                        {
                            "type": "number"
                        },
                    ],
                },
            },
            "maxProperties": 100,
            "additionalProperties": False,
        },
        "group": {
            "type": ["object", "null"],
            "properties": {
                "type": {
                    "type": "string",
                    "pattern": "^([A-Z][a-zA-Z]*)+$",
                    "maxLength": 50,
                },
                "is_group": {
                    "type": "boolean",
                    "enum": [True],
                },
                "id": {
                    "type": ["string", "integer"],
                    "pattern": "^[ -~]+$",
                    "maxLength": 250,
                    "minLength": 1,
                },
                "display_name": {
                    "type": "string",
                    "maxLength": 250,
                    "minLength": 1,
                },
                "attributes": {
                    "type": "object",
                    "patternProperties": {
                        "^[a-zA-Z][a-zA-Z_]{0,48}[a-zA-Z]$": {
                            "oneOf": [
                                {
                                    "type": "string",
                                    "maxLength": 3000,
                                },
                                {
                                    "type": "boolean"
                                },
                                {
                                    "type": "number"
                                },
                            ],
                        },
                    },
                    "maxProperties": 100,
                    "additionalProperties": False,
                },
            },
            "required": ["id"],
            "additionalProperties": False,
        },
    },
    "required": ["id"],
    "additionalProperties": False,
}

SERVER_URL = 'https://api.airshiphq.com'
IDENTIFY_ENDPOINT = '{}/v1/identify'.format(SERVER_URL)
GATING_INFO_ENDPOINT = '{}/v1/gating-info'.format(SERVER_URL)
PLATFORM = 'python'

SDK_VERSION = '{}:{}'.format(PLATFORM, '1.1.12')

CONTROL_TYPE_BOOLEAN = 'boolean'
CONTROL_TYPE_MULTIVARIATE = 'multivariate'

DISTRIBUTION_TYPE_RULE_BASED = 'R'
DISTRIBUTION_TYPE_PERCENTAGE_BASED = 'P'

OBJECT_ATTRIBUTE_TYPE_STRING = 'STRING'
OBJECT_ATTRIBUTE_TYPE_INT = 'INT'
OBJECT_ATTRIBUTE_TYPE_FLOAT = 'FLOAT'
OBJECT_ATTRIBUTE_TYPE_BOOLEAN = 'BOOLEAN'
OBJECT_ATTRIBUTE_TYPE_DATE = 'DATE'
OBJECT_ATTRIBUTE_TYPE_DATETIME = 'DATETIME'

RULE_OPERATOR_TYPE_IS = 'IS'
RULE_OPERATOR_TYPE_IS_NOT = 'IS_NOT'
RULE_OPERATOR_TYPE_IN = 'IN'
RULE_OPERATOR_TYPE_NOT_IN = 'NOT_IN'
RULE_OPERATOR_TYPE_LT = 'LT'
RULE_OPERATOR_TYPE_LTE = 'LTE'
RULE_OPERATOR_TYPE_GT = 'GT'
RULE_OPERATOR_TYPE_GTE = 'GTE'
RULE_OPERATOR_TYPE_FROM = 'FROM'
RULE_OPERATOR_TYPE_UNTIL = 'UNTIL'
RULE_OPERATOR_TYPE_AFTER = 'AFTER'
RULE_OPERATOR_TYPE_BEFORE = 'BEFORE'

def get_hashed_value(s):
    m = hashlib.md5()
    m.update(s.encode('utf-8'))
    return (float(int(m.hexdigest(), 16)) / float((1 << 128) - 1))

class Airship:

    SDK_ID = ''.join([choice(ascii_lowercase + ascii_uppercase + digits) for _ in range(6)])

    def __init__(self, options):
        self.api_key = options.get('api_key')
        self.env_key = options.get('env_key')
        self.timeout = 10

        self.polling_interval = 60
        self.ingestion_interval = 60

        self.polling_thread = None
        self.ingestion_thread = None

        self.gating_info = None
        self.gating_info_map = None

        self.last_ingestion_timestamp = 0
        self.ingestion_tasks = []

        self.ingestion_batch = []
        self.ingestion_max_batch_size = 500

        self.init_lock = Lock()
        self.ingestion_batch_lock = Lock()

        self.first_ingestion = True

        def kill(*args):
            if self.polling_thread is not None:
                self.polling_thread.cancel()

            if self.ingestion_thread is not None:
                self.ingestion_thread.cancel()

        signal.signal(signal.SIGTERM, kill)
        signal.signal(signal.SIGINT, kill)


    def init(self):
        self.init_lock.acquire()
        if self.polling_thread is None:
            self._poll()
            self.polling_thread = self._create_poller()
            self.polling_thread.start()

        if self.ingestion_thread is None:
            self.ingestion_thread = self._create_ingestor()
            self.ingestion_thread.start()
        self.init_lock.release()
        return self

    def _get_gating_info_map(self, gating_info):
        info_map = {}

        controls = gating_info['controls']

        for control in controls:
            control_info = {}

            control_info['id'] = control['id']
            control_info['is_on'] = control['is_on']
            control_info['rule_based_distribution_default_variation'] = control['rule_based_distribution_default_variation']
            control_info['rule_sets'] = control['rule_sets']
            control_info['distributions'] = control['distributions']
            control_info['type'] = control['type']
            control_info['default_variation'] = control['default_variation']

            enablements = control['enablements']
            enablements_info = {}

            for enablement in enablements:
                client_identities_map = enablements_info.get(enablement['client_object_type_name'])

                if client_identities_map is None:
                    enablements_info[enablement['client_object_type_name']] = {}

                enablements_info[enablement['client_object_type_name']][enablement['client_object_identity']] = (enablement['is_enabled'], enablement['variation'])

            control_info['enablements_info'] = enablements_info

            info_map[control['short_name']] = control_info

        return info_map

    def _poll(self):
        try:
            url = '{}/{}'.format(GATING_INFO_ENDPOINT, self.env_key)
            headers = {'api-key': self.api_key}

            response = requests.get(url, headers=headers, timeout=self.timeout)

            if response.status_code == 200:
                gating_info = json.loads(response.text)

                if gating_info.get('server_info') == 'maintenance':
                    print('Airship is currently going through maintenance')
                    return

                gating_info_map = self._get_gating_info_map(gating_info)
                self.gating_info = gating_info
                self.gating_info_map = gating_info_map

                if 'polling_interval' in gating_info:
                    self.polling_interval = gating_info['polling_interval']

                if 'ingestion_interval' in gating_info:
                    self.ingestion_interval = gating_info['ingestion_interval']

            else:
                print('Failed to connect to Airship server')
        except Exception as e:
            print('Failed to connect to Airship server')

    def _create_poller(self):
        def poll():
            self._poll()

            self.polling_thread = Timer(self.polling_interval, poll)
            self.polling_thread.start()

        return Timer(0, poll)

    def _create_ingestor(self):
        def trigger_ingestion():
            now = time.time()
            if now - self.last_ingestion_timestamp >= self.ingestion_interval:
                processed = self._process_batch(0)
                if processed:
                    self.last_ingestion_timestamp = now

            self.ingestion_thread = Timer(self.ingestion_interval, trigger_ingestion)
            self.ingestion_thread.start()

        return Timer(0, trigger_ingestion)

    def _create_processor(self, payload):
        def process():
            url = IDENTIFY_ENDPOINT
            headers = {'api-key': self.api_key, 'Content-Type': 'application/json'}

            data = json.dumps(
                {
                    'env_key': self.env_key,
                    'objects': payload,
                }
            )

            response = requests.post(url, headers=headers, data=data, timeout=self.timeout)
        return Timer(0, process)

    def _process_batch(self, limit, gate_stats=None):
        # This is sort of a weird function.
        # We process the batch if the batch size
        # is more than limit. The second param
        # allows for an additional gate_states to
        # be inserted before the processing check
        # is performed.

        processed = False
        self.ingestion_batch_lock.acquire()

        if gate_stats is not None:
            self.ingestion_batch.append(gate_stats)

        if len(self.ingestion_batch) > limit or (self.first_ingestion and len(self.ingestion_batch) > 0):
            self.first_ingestion = False
            new_ingestion_tasks = []
            for task in self.ingestion_tasks:
                if task.is_alive():
                    new_ingestion_tasks.append(task)

            payload = self.ingestion_batch
            self.ingestion_batch = []
            task = self._create_processor(payload)
            task.start()
            new_ingestion_tasks.append(task)
            self.ingestion_tasks = new_ingestion_tasks
            processed = True

        self.ingestion_batch_lock.release()
        return processed

    def _ingest_async(self, gate_stats):
        processed = self._process_batch(self.ingestion_max_batch_size - 1, gate_stats)
        if processed:
            now = time.time()
            self.last_ingestion_timestamp = now

    def _satisfies_rule(self, rule, obj):
        attribute_type = rule['attribute_type']
        operator = rule['operator']
        attribute_name = rule['attribute_name']
        value = rule['value']
        value_list = rule['value_list']

        if 'attributes' not in obj or attribute_name not in obj['attributes']:
            return False

        attribute_val = obj['attributes'][attribute_name]

        if attribute_type == OBJECT_ATTRIBUTE_TYPE_STRING:
            if operator == RULE_OPERATOR_TYPE_IS:
                return attribute_val == value
            elif operator == RULE_OPERATOR_TYPE_IS_NOT:
                return attribute_val != value
            elif operator == RULE_OPERATOR_TYPE_IN:
                return attribute_val in value_list
            elif operator == RULE_OPERATOR_TYPE_NOT_IN:
                return attribute_val not in value_list
            else:
                return False
        elif attribute_type == OBJECT_ATTRIBUTE_TYPE_INT:
            value = value and int(value)
            value_list = value_list and [int(v) for v in value_list]

            if operator == RULE_OPERATOR_TYPE_IS:
                return attribute_val == value
            elif operator == RULE_OPERATOR_TYPE_IS_NOT:
                return attribute_val != value
            elif operator == RULE_OPERATOR_TYPE_IN:
                return attribute_val in value_list
            elif operator == RULE_OPERATOR_TYPE_NOT_IN:
                return attribute_val not in value_list
            elif operator == RULE_OPERATOR_TYPE_LT:
                return attribute_val < value
            elif operator == RULE_OPERATOR_TYPE_LTE:
                return attribute_val <= value
            elif operator == RULE_OPERATOR_TYPE_GT:
                return attribute_val > value
            elif operator == RULE_OPERATOR_TYPE_GTE:
                return attribute_val >= value
            else:
                return False
        elif attribute_type == OBJECT_ATTRIBUTE_TYPE_FLOAT:
            value = value and float(value)
            value_list = value_list and [float(v) for v in value_list]

            if operator == RULE_OPERATOR_TYPE_IS:
                return attribute_val == value
            elif operator == RULE_OPERATOR_TYPE_IS_NOT:
                return attribute_val != value
            elif operator == RULE_OPERATOR_TYPE_IN:
                return attribute_val in value_list
            elif operator == RULE_OPERATOR_TYPE_NOT_IN:
                return attribute_val not in value_list
            elif operator == RULE_OPERATOR_TYPE_LT:
                return attribute_val < value
            elif operator == RULE_OPERATOR_TYPE_LTE:
                return attribute_val <= value
            elif operator == RULE_OPERATOR_TYPE_GT:
                return attribute_val > value
            elif operator == RULE_OPERATOR_TYPE_GTE:
                return attribute_val >= value
            else:
                return False
        elif attribute_type == OBJECT_ATTRIBUTE_TYPE_BOOLEAN:
            value = (value == 'true')
            if operator == RULE_OPERATOR_TYPE_IS:
                return attribute_val == value
            elif operator == RULE_OPERATOR_TYPE_IS_NOT:
                return attribute_val != value
            else:
                return False
        elif attribute_type == OBJECT_ATTRIBUTE_TYPE_DATE:
            unix_timestamp = None
            try:
                unix_timestamp = time.mktime(parse_date(attribute_val).timetuple())
            except Exception as e:
                return False

            iso_format = parse_date(attribute_val).isoformat()

            if not iso_format.endswith('T00:00:00'):
                return False

            value = value and time.mktime(parse_date(value).timetuple())
            value_list = value_list and [time.mktime(parse_date(v).timetuple()) for v in value_list]

            attribute_val = unix_timestamp

            if operator == RULE_OPERATOR_TYPE_IS:
                return attribute_val == value
            elif operator == RULE_OPERATOR_TYPE_IS_NOT:
                return attribute_val != value
            elif operator == RULE_OPERATOR_TYPE_IN:
                return attribute_val in value_list
            elif operator == RULE_OPERATOR_TYPE_NOT_IN:
                return attribute_val not in value_list
            elif operator == RULE_OPERATOR_TYPE_FROM:
                return attribute_val >= value
            elif operator == RULE_OPERATOR_TYPE_UNTIL:
                return attribute_val <= value
            elif operator == RULE_OPERATOR_TYPE_AFTER:
                return attribute_val > value
            elif operator == RULE_OPERATOR_TYPE_BEFORE:
                return attribute_val < value
            else:
                return False
        elif attribute_type == OBJECT_ATTRIBUTE_TYPE_DATETIME:
            unix_timestamp = None
            try:
                unix_timestamp = time.mktime(parse_date(attribute_val).astimezone(tz.gettz('UTC')).replace(tzinfo=None).timetuple())
            except Exception as e:
                return False

            value = value and time.mktime(parse_date(value).astimezone(tz.gettz('UTC')).replace(tzinfo=None).timetuple())
            value_list = value_list and [time.mktime(parse_date(v).astimezone(tz.gettz('UTC')).replace(tzinfo=None).timetuple()) for v in value_list]

            attribute_val = unix_timestamp

            if operator == RULE_OPERATOR_TYPE_IS:
                return attribute_val == value
            elif operator == RULE_OPERATOR_TYPE_IS_NOT:
                return attribute_val != value
            elif operator == RULE_OPERATOR_TYPE_IN:
                return attribute_val in value_list
            elif operator == RULE_OPERATOR_TYPE_NOT_IN:
                return attribute_val not in value_list
            elif operator == RULE_OPERATOR_TYPE_FROM:
                return attribute_val >= value
            elif operator == RULE_OPERATOR_TYPE_UNTIL:
                return attribute_val <= value
            elif operator == RULE_OPERATOR_TYPE_AFTER:
                return attribute_val > value
            elif operator == RULE_OPERATOR_TYPE_BEFORE:
                return attribute_val < value
            else:
                return False
        else:
            return False

    def _get_gate_values_for_object(self, control_info, obj):
        if obj['type'] in control_info['enablements_info']:
            if obj['id'] in control_info['enablements_info'][obj['type']]:
                (is_enabled, variation) = control_info['enablements_info'][obj['type']][obj['id']]
                return {
                    'is_enabled': is_enabled,
                    'variation': variation,
                    'is_eligible': is_enabled,
                    '_from_enablement': True,
                }

        sampled_inside_base_population = False
        is_eligible = False
        for rule_set in control_info['rule_sets']:
            if sampled_inside_base_population:
                break

            rules = rule_set['rules']

            if rule_set['client_object_type_name'] != obj['type']:
                continue

            satisfies_all_rules = True
            for rule in rules:
                satisfies_all_rules = satisfies_all_rules and self._satisfies_rule(rule, obj)

            if satisfies_all_rules:
                is_eligible = True
                hash_key = 'SAMPLING:control_{}:env_{}:rule_set_{}:client_object_{}_{}'.format(
                    control_info['id'],
                    self.gating_info['env']['id'],
                    rule_set['id'],
                    obj['type'],
                    obj['id'],
                )
                if get_hashed_value(hash_key) <= rule_set['sampling_percentage']:
                    sampled_inside_base_population = True

        if not sampled_inside_base_population:
            return {
                'is_enabled': False,
                'variation': None,
                'is_eligible': is_eligible,
            }

        if control_info['type'] == CONTROL_TYPE_BOOLEAN:
            return {
                'is_enabled': True,
                'variation': None,
                'is_eligible': True,
            }
        elif control_info['type'] == CONTROL_TYPE_MULTIVARIATE:
            if len(control_info['distributions']) == 0:
                return {
                    'is_enabled': True,
                    'variation': control_info['default_variation'],
                    'is_eligible': True,
                }

            percentage_based_distributions = [d for d in control_info['distributions'] if d['type'] == DISTRIBUTION_TYPE_PERCENTAGE_BASED]
            rule_based_distributions = [d for d in control_info['distributions'] if d['type'] == DISTRIBUTION_TYPE_RULE_BASED]

            if len(percentage_based_distributions) != 0 and len(rule_based_distributions) != 0:
                print('Rule integrity error: please contact support@airshiphq.com')
                return {
                    'is_enabled': False,
                    'variation': None,
                    'is_eligible': False,
                }

            if len(percentage_based_distributions) != 0:
                delta = 0.0001
                sum_percentages = 0.0
                running_percentages = []
                for distribution in percentage_based_distributions:
                    sum_percentages += distribution['percentage']
                    if len(running_percentages) == 0:
                        running_percentages.append(distribution['percentage'])
                    else:
                        running_percentages.append(running_percentages[len(running_percentages) - 1] + distribution['percentage'])

                if abs(1.0 - sum_percentages) > delta:
                    print('Rule integrity error: please contact support@airshiphq.com')
                    return {
                        'is_enabled': False,
                        'variation': None,
                        'is_eligible': False,
                    }

                hash_key = 'DISTRIBUTION:control_{}:env_{}:client_object_{}_{}'.format(
                    control_info['id'],
                    self.gating_info['env']['id'],
                    obj['type'],
                    obj['id'],
                )
                hashed_percentage = get_hashed_value(hash_key)

                for (i, percentage) in enumerate(running_percentages):
                    if hashed_percentage <= percentage:
                        return {
                            'is_enabled': True,
                            'variation': percentage_based_distributions[i]['variation'],
                            'is_eligible': True,
                        }

                return {
                    'is_enabled': True,
                    'variation': percentage_based_distributions[len(percentage_based_distributions) - 1]['variation'],
                    'is_eligible': True,
                }
            else:
                for distribution in rule_based_distributions:
                    rule_set = distribution['rule_set']
                    rules = rule_set['rules']

                    if rule_set['client_object_type_name'] != obj['type']:
                        continue

                    satisfies_all_rules = True
                    for rule in rules:
                        satisfies_all_rules = satisfies_all_rules and self._satisfies_rule(rule, obj)

                    if satisfies_all_rules:
                        return {
                            'is_enabled': True,
                            'variation': distribution['variation'],
                            'is_eligible': True,
                        }

                return {
                    'is_enabled': True,
                    'variation': control_info['rule_based_distribution_default_variation'] or control_info['default_variation'],
                    'is_eligible': True,
                    '_rule_based_default_variation': True,
                }
        else:
            return {
                'is_enabled': False,
                'variation': None,
                'is_eligible': False,
            }

    def _get_gate_values(self, control_short_name, obj):
        if self.gating_info_map.get(control_short_name) is None:
            return {
                'is_enabled': False,
                'variation': None,
                'is_eligible': False,
                '_should_send_stats': False,
            }

        control_info = self.gating_info_map[control_short_name]

        if not control_info['is_on']:
            return {
                'is_enabled': False,
                'variation': None,
                'is_eligible': False,
                '_should_send_stats': True,
            }

        group = obj.get('group')

        result = self._get_gate_values_for_object(control_info, obj)

        if group is not None:
            if group.get('type') is None:
                group['type'] = '{}Group'.format(obj['type'])
                group['is_group'] = True

            group_result = self._get_gate_values_for_object(control_info, group)

            if result.get('_from_enablement') is True and not result['is_enabled']:
                # Do nothing
                pass
            elif result.get('_from_enablement') is not True and group_result.get('_from_enablement') is True and not group_result['is_enabled']:
                result['is_enabled'] = group_result['is_enabled']
                result['variation'] = group_result['variation']
                result['is_eligible'] = group_result['is_eligible']
            elif result['is_enabled']:
                if result.get('_rule_based_default_variation') is True:
                    if group_result['is_enabled']:
                        result['is_enabled'] = group_result['is_enabled']
                        result['variation'] = group_result['variation']
                        result['is_eligible'] = group_result['is_eligible']
                    else:
                        # Do nothing
                        pass
                else:
                    # Do nothing
                    pass
            elif group_result['is_enabled']:
                result['is_enabled'] = group_result['is_enabled']
                result['variation'] = group_result['variation']
                result['is_eligible'] = group_result['is_eligible']
            else:
                # Do nothing
                pass

        result['_should_send_stats'] = True
        return result

    def _clone_object(self, obj):
        clone = copy.deepcopy(obj)
        return clone

    def _validate_nesting(self, obj):
        if obj.get('is_group') is True and 'group' in obj:
            return 'A group cannot be nested inside another group'

    def _validate_anonymous(self, obj):
        if obj.get('is_anonymous') is True and 'group' in obj:
            return 'An anonymous object cannot belong to a group'

        if obj.get('is_group') is True and obj.get('is_anonymous') is True:
            return 'A group cannot be anonymous'

    def _maybe_transform_id(self, obj):
        if isinstance(obj['id'], (int, long)):
            id_str = str(obj['id'])
            if len(id_str) > 250:
                return 'Integer id must have 250 digits or less'
            obj['id'] = id_str

        group = obj.get('group')

        if group is not None:
            if isinstance(group['id'], (int, long)):
                id_str = str(group['id'])
                if len(id_str) > 250:
                    return 'Integer id must have 250 digits or less'
                group['id'] = id_str

    def _enrich_with_metadata(self, control_short_name, stats):
        control_info = self.gating_info_map.get(control_short_name)

        if control_info is not None:
            stats['sdk_gate_control_id'] = control_info['id']

        stats['sdk_env_id'] = self.gating_info['env']['id']

    def _maybe_add_fields(self, obj):
        if 'type' not in obj:
            obj['type'] = 'User'

        if 'display_name' not in obj:
            obj['display_name'] = str(obj['id'])

        group = obj.get('group')

        if group is not None:
            if 'display_name' not in group:
                group['display_name'] = str(group['id'])

    def is_enabled(self, control_short_name, obj, default_value=False):
        try:
            jsonschema.validate(obj, SCHEMA)
        except Exception as e:
            print(e.message)
            return default_value

        obj = self._clone_object(obj)

        self._maybe_add_fields(obj)

        error = self._validate_nesting(obj) or self._validate_anonymous(obj) or self._maybe_transform_id(obj)

        if error is not None:
            print(error)
            return default_value

        if self.gating_info_map is None:
            return default_value

        gate_timestamp = datetime.utcnow().replace(tzinfo=tz.gettz('UTC')).isoformat()

        start = time.time()

        gate_values = self._get_gate_values(control_short_name, obj)
        is_enabled = gate_values['is_enabled']
        variation = gate_values['variation']
        is_eligible = gate_values['is_eligible']
        _should_send_stats = gate_values['_should_send_stats']

        finish = time.time()

        if _should_send_stats:
            sdk_gate_timestamp = gate_timestamp
            sdk_gate_latency = '{}us'.format((finish - start) * 1000 * 1000)
            sdk_version = SDK_VERSION

            stats = {}
            stats['sdk_gate_control_short_name'] = control_short_name
            stats['sdk_gate_timestamp'] = sdk_gate_timestamp
            stats['sdk_gate_latency'] = sdk_gate_latency

            stats['sdk_gate_value'] = is_enabled
            stats['sdk_gate_variation'] = variation
            stats['sdk_gate_eligibility'] = is_eligible
            stats['sdk_gate_type'] = 'value'

            self._enrich_with_metadata(control_short_name, stats)

            stats['sdk_version'] = sdk_version
            stats['sdk_id'] = self.SDK_ID

            obj['stats'] = stats

            self._ingest_async(obj)

        return is_enabled

    def get_variation(self, control_short_name, obj, default_value=None):
        try:
            jsonschema.validate(obj, SCHEMA)
        except Exception as e:
            print(e.message)
            return default_value

        obj = self._clone_object(obj)

        self._maybe_add_fields(obj)

        error = self._validate_nesting(obj) or self._validate_anonymous(obj) or self._maybe_transform_id(obj)

        if error is not None:
            print(error)
            return default_value

        if self.gating_info_map is None:
            return default_value

        gate_timestamp = datetime.utcnow().replace(tzinfo=tz.gettz('UTC')).isoformat()

        start = time.time()

        gate_values = self._get_gate_values(control_short_name, obj)
        is_enabled = gate_values['is_enabled']
        variation = gate_values['variation']
        is_eligible = gate_values['is_eligible']
        _should_send_stats = gate_values['_should_send_stats']

        finish = time.time()

        if _should_send_stats:
            sdk_gate_timestamp = gate_timestamp
            sdk_gate_latency = '{}us'.format((finish - start) * 1000 * 1000)
            sdk_version = SDK_VERSION

            stats = {}
            stats['sdk_gate_control_short_name'] = control_short_name
            stats['sdk_gate_timestamp'] = sdk_gate_timestamp
            stats['sdk_gate_latency'] = sdk_gate_latency

            stats['sdk_gate_value'] = is_enabled
            stats['sdk_gate_variation'] = variation
            stats['sdk_gate_eligibility'] = is_eligible
            stats['sdk_gate_type'] = 'variation'

            self._enrich_with_metadata(control_short_name, stats)

            stats['sdk_version'] = sdk_version
            stats['sdk_id'] = self.SDK_ID

            obj['stats'] = stats

            self._ingest_async(obj)

        return variation

    def is_eligible(self, control_short_name, obj, default_value=False):
        try:
            jsonschema.validate(obj, SCHEMA)
        except Exception as e:
            print(e.message)
            return default_value

        obj = self._clone_object(obj)

        self._maybe_add_fields(obj)

        error = self._validate_nesting(obj) or self._validate_anonymous(obj) or self._maybe_transform_id(obj)

        if error is not None:
            print(error)
            return default_value

        if self.gating_info_map is None:
            return default_value

        gate_timestamp = datetime.utcnow().replace(tzinfo=tz.gettz('UTC')).isoformat()

        start = time.time()

        gate_values = self._get_gate_values(control_short_name, obj)
        is_enabled = gate_values['is_enabled']
        variation = gate_values['variation']
        is_eligible = gate_values['is_eligible']
        _should_send_stats = gate_values['_should_send_stats']

        finish = time.time()

        if _should_send_stats:
            sdk_gate_timestamp = gate_timestamp
            sdk_gate_latency = '{}us'.format((finish - start) * 1000 * 1000)
            sdk_version = SDK_VERSION

            stats = {}
            stats['sdk_gate_control_short_name'] = control_short_name
            stats['sdk_gate_timestamp'] = sdk_gate_timestamp
            stats['sdk_gate_latency'] = sdk_gate_latency

            stats['sdk_gate_value'] = is_enabled
            stats['sdk_gate_variation'] = variation
            stats['sdk_gate_eligibility'] = is_eligible
            stats['sdk_gate_type'] = 'eligibility'

            self._enrich_with_metadata(control_short_name, stats)

            stats['sdk_version'] = sdk_version
            stats['sdk_id'] = self.SDK_ID

            obj['stats'] = stats

            self._ingest_async(obj)

        return is_eligible
