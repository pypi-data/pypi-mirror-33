# Copyright 2017 StreamSets Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Various utilities to be used by other modules."""

import random
from collections import defaultdict


def infinitedict():
    """
    Infinitely nested dictionary. Useful for creating nested dictionaries.
    Example:
        my_dict = infinitedict()
        my_dict['dimension1']['dimension2']['dimension3'] = 'dimension 3 value'
    Results my_dict to a dictionary value as:
        {
          "dimension1": {
            "dimension2": {
              "dimension3": "dimension 3 value"
            }
          }
        }
    """
    return defaultdict(infinitedict)


def get_random_string(characters, length=8):
    """
    Returns a string of the requested length consisting of random combinations of the given
    sequence of string characters.
    """
    return ''.join(random.choice(characters) for _ in range(length))


def yaml_merge_collections(json):
    """YAML has a missing feature: ability to extend lists. This allows extending the lists, as well as the maps of
    the elements referenced by an alias. Courtesy of https://bit.ly/2HMfrWs with all the details.

    Example YAML:
        defaults: &defaults
          sites:
            - www.foo.com
            - www.bar.com

        setup1:
          <<: *defaults
          sites+:
            - www.baz.com
    Results of this function:
        defaults:
          sites:
            - www.foo.com
            - www.bar.com

        setup1:
          sites:
            - www.foo.com
            - www.bar.com
            - www.baz.com
    """
    def _trailing_plus_count(s):
        for i in range(0, len(s)):
            if s[-i-1] != '+':
                return i
        return len(s)

    def _extend_list_or_dict(json, json2, key, merge_lists=True):
        if type(json) == dict and type(json2) == dict:
            for k2, v2 in json2.items():
               json[k2] = v2
            return json
        elif merge_lists and type(json) == list and type(json2) == list:
            json.extend(json2)
            return json
        return json2

    if type(json) == dict:
        to_merge = None
        for k in json.keys():
            if type(k) == str and _trailing_plus_count(k) > 0:
                if not to_merge:
                    to_merge = [k]
                else:
                    to_merge.append(k)
        if to_merge:
            for k2 in sorted(to_merge, key=_trailing_plus_count):
                v2 = json[k2]
                k = k2[0: len(k2) - _trailing_plus_count(k2)]
                if len(k) > 0:
                    if k in json:
                        v = json[k]
                        json[k] = _extend_list_or_dict(v, v2, k)
                    else:
                        json[k] = v2
                    json.pop(k2)
        for v in json.values():
            if type(v) in (list, dict):
                yaml_merge_collections(v)
    elif type(json) == list:
        for item in json:
            yaml_merge_collections(item)
