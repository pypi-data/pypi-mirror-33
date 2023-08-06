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
class UpdateUserRequest(RpcRequest):

	def __init__(self):
		RpcRequest.__init__(self, 'Ims', '2017-04-30', 'UpdateUser','ims')

	def get_NewWorkPhone(self):
		return self.get_query_params().get('NewWorkPhone')

	def set_NewWorkPhone(self,NewWorkPhone):
		self.add_query_param('NewWorkPhone',NewWorkPhone)

	def get_NewDisplayName(self):
		return self.get_query_params().get('NewDisplayName')

	def set_NewDisplayName(self,NewDisplayName):
		self.add_query_param('NewDisplayName',NewDisplayName)

	def get_NewMobilePhone(self):
		return self.get_query_params().get('NewMobilePhone')

	def set_NewMobilePhone(self,NewMobilePhone):
		self.add_query_param('NewMobilePhone',NewMobilePhone)

	def get_NewEnabled(self):
		return self.get_query_params().get('NewEnabled')

	def set_NewEnabled(self,NewEnabled):
		self.add_query_param('NewEnabled',NewEnabled)

	def get_NewManagerUserId(self):
		return self.get_query_params().get('NewManagerUserId')

	def set_NewManagerUserId(self,NewManagerUserId):
		self.add_query_param('NewManagerUserId',NewManagerUserId)

	def get_NewWorkAddress(self):
		return self.get_query_params().get('NewWorkAddress')

	def set_NewWorkAddress(self,NewWorkAddress):
		self.add_query_param('NewWorkAddress',NewWorkAddress)

	def get_UserId(self):
		return self.get_query_params().get('UserId')

	def set_UserId(self,UserId):
		self.add_query_param('UserId',UserId)

	def get_NewOrgUnitId(self):
		return self.get_query_params().get('NewOrgUnitId')

	def set_NewOrgUnitId(self,NewOrgUnitId):
		self.add_query_param('NewOrgUnitId',NewOrgUnitId)

	def get_UserPrincipalName(self):
		return self.get_query_params().get('UserPrincipalName')

	def set_UserPrincipalName(self,UserPrincipalName):
		self.add_query_param('UserPrincipalName',UserPrincipalName)

	def get_NewComments(self):
		return self.get_query_params().get('NewComments')

	def set_NewComments(self,NewComments):
		self.add_query_param('NewComments',NewComments)

	def get_NewHomeAddress(self):
		return self.get_query_params().get('NewHomeAddress')

	def set_NewHomeAddress(self,NewHomeAddress):
		self.add_query_param('NewHomeAddress',NewHomeAddress)

	def get_NewEmployeeType(self):
		return self.get_query_params().get('NewEmployeeType')

	def set_NewEmployeeType(self,NewEmployeeType):
		self.add_query_param('NewEmployeeType',NewEmployeeType)

	def get_NewManagerUserPrincipalName(self):
		return self.get_query_params().get('NewManagerUserPrincipalName')

	def set_NewManagerUserPrincipalName(self,NewManagerUserPrincipalName):
		self.add_query_param('NewManagerUserPrincipalName',NewManagerUserPrincipalName)

	def get_NewEmail(self):
		return self.get_query_params().get('NewEmail')

	def set_NewEmail(self,NewEmail):
		self.add_query_param('NewEmail',NewEmail)

	def get_NewJobTitle(self):
		return self.get_query_params().get('NewJobTitle')

	def set_NewJobTitle(self,NewJobTitle):
		self.add_query_param('NewJobTitle',NewJobTitle)

	def get_NewUserPrincipalName(self):
		return self.get_query_params().get('NewUserPrincipalName')

	def set_NewUserPrincipalName(self,NewUserPrincipalName):
		self.add_query_param('NewUserPrincipalName',NewUserPrincipalName)

	def get_NewOrgUnitPath(self):
		return self.get_query_params().get('NewOrgUnitPath')

	def set_NewOrgUnitPath(self,NewOrgUnitPath):
		self.add_query_param('NewOrgUnitPath',NewOrgUnitPath)

	def get_NewEmployeeId(self):
		return self.get_query_params().get('NewEmployeeId')

	def set_NewEmployeeId(self,NewEmployeeId):
		self.add_query_param('NewEmployeeId',NewEmployeeId)