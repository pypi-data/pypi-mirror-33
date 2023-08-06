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
class CreateOrgUnitRequest(RpcRequest):

	def __init__(self):
		RpcRequest.__init__(self, 'Ims', '2017-04-30', 'CreateOrgUnit','ims')

	def get_OrgUnitName(self):
		return self.get_query_params().get('OrgUnitName')

	def set_OrgUnitName(self,OrgUnitName):
		self.add_query_param('OrgUnitName',OrgUnitName)

	def get_Comments(self):
		return self.get_query_params().get('Comments')

	def set_Comments(self,Comments):
		self.add_query_param('Comments',Comments)

	def get_ParentOrgUnitId(self):
		return self.get_query_params().get('ParentOrgUnitId')

	def set_ParentOrgUnitId(self,ParentOrgUnitId):
		self.add_query_param('ParentOrgUnitId',ParentOrgUnitId)

	def get_ExternalId(self):
		return self.get_query_params().get('ExternalId')

	def set_ExternalId(self,ExternalId):
		self.add_query_param('ExternalId',ExternalId)

	def get_ParentOrgUnitPath(self):
		return self.get_query_params().get('ParentOrgUnitPath')

	def set_ParentOrgUnitPath(self,ParentOrgUnitPath):
		self.add_query_param('ParentOrgUnitPath',ParentOrgUnitPath)