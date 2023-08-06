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
class ListUsersRequest(RpcRequest):

	def __init__(self):
		RpcRequest.__init__(self, 'Ims', '2017-04-30', 'ListUsers','ims')

	def get_Filter(self):
		return self.get_query_params().get('Filter')

	def set_Filter(self,Filter):
		self.add_query_param('Filter',Filter)

	def get_ScopeType(self):
		return self.get_query_params().get('ScopeType')

	def set_ScopeType(self,ScopeType):
		self.add_query_param('ScopeType',ScopeType)

	def get_OrgUnit(self):
		return self.get_query_params().get('OrgUnit')

	def set_OrgUnit(self,OrgUnit):
		self.add_query_param('OrgUnit',OrgUnit)

	def get_Marker(self):
		return self.get_query_params().get('Marker')

	def set_Marker(self,Marker):
		self.add_query_param('Marker',Marker)

	def get_UserType(self):
		return self.get_query_params().get('UserType')

	def set_UserType(self,UserType):
		self.add_query_param('UserType',UserType)

	def get_OrderBy(self):
		return self.get_query_params().get('OrderBy')

	def set_OrderBy(self,OrderBy):
		self.add_query_param('OrderBy',OrderBy)

	def get_IsDesc(self):
		return self.get_query_params().get('IsDesc')

	def set_IsDesc(self,IsDesc):
		self.add_query_param('IsDesc',IsDesc)

	def get_MaxItems(self):
		return self.get_query_params().get('MaxItems')

	def set_MaxItems(self,MaxItems):
		self.add_query_param('MaxItems',MaxItems)