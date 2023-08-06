# Copyright 2018 Siu-Kei Muk (David). All Rights Reserved.
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
# ==============================================================================
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


def get_cast():
  sig = {'object': object,
         'encoding': str,
         'errors': str}

  def cast(object, encoding=None, errors=None):
    if encoding is None and errors is None:
      return str(object)
    kwargs = {}
    if encoding is not None: kwargs['encoding'] = encoding
    if errors is not None: kwargs['errors'] = errors
    return str(object, **kwargs)

  return cast, sig, {'object': ''}
