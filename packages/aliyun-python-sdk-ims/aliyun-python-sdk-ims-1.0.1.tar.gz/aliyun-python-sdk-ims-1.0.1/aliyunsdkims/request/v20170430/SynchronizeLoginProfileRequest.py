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
class SynchronizeLoginProfileRequest(RpcRequest):

	def __init__(self):
		RpcRequest.__init__(self, 'Ims', '2017-04-30', 'SynchronizeLoginProfile','ims')

	def get_UserPrincipalName(self):
		return self.get_query_params().get('UserPrincipalName')

	def set_UserPrincipalName(self,UserPrincipalName):
		self.add_query_param('UserPrincipalName',UserPrincipalName)

	def get_Password(self):
		return self.get_query_params().get('Password')

	def set_Password(self,Password):
		self.add_query_param('Password',Password)

	def get_Salt(self):
		return self.get_query_params().get('Salt')

	def set_Salt(self,Salt):
		self.add_query_param('Salt',Salt)

	def get_PasswordResetRequired(self):
		return self.get_query_params().get('PasswordResetRequired')

	def set_PasswordResetRequired(self,PasswordResetRequired):
		self.add_query_param('PasswordResetRequired',PasswordResetRequired)

	def get_Plain(self):
		return self.get_query_params().get('Plain')

	def set_Plain(self,Plain):
		self.add_query_param('Plain',Plain)

	def get_LoginProfileUpdateDate(self):
		return self.get_query_params().get('LoginProfileUpdateDate')

	def set_LoginProfileUpdateDate(self,LoginProfileUpdateDate):
		self.add_query_param('LoginProfileUpdateDate',LoginProfileUpdateDate)

	def get_LoginProfileCreateDate(self):
		return self.get_query_params().get('LoginProfileCreateDate')

	def set_LoginProfileCreateDate(self,LoginProfileCreateDate):
		self.add_query_param('LoginProfileCreateDate',LoginProfileCreateDate)

	def get_MfaBindRequired(self):
		return self.get_query_params().get('MfaBindRequired')

	def set_MfaBindRequired(self,MfaBindRequired):
		self.add_query_param('MfaBindRequired',MfaBindRequired)

	def get_PasswordType(self):
		return self.get_query_params().get('PasswordType')

	def set_PasswordType(self,PasswordType):
		self.add_query_param('PasswordType',PasswordType)