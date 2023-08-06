# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from aliyunsdkcore.request import RpcRequest
class EnableDirectoryRequest(RpcRequest):

	def __init__(self):
		RpcRequest.__init__(self, 'Ims', '2017-04-30', 'EnableDirectory','ims')

	def get_NewDisplayName(self):
		return self.get_query_params().get('NewDisplayName')

	def set_NewDisplayName(self,NewDisplayName):
		self.add_query_param('NewDisplayName',NewDisplayName)

	def get_NewDirectoryName(self):
		return self.get_query_params().get('NewDirectoryName')

	def set_NewDirectoryName(self,NewDirectoryName):
		self.add_query_param('NewDirectoryName',NewDirectoryName)