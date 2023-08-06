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
class CreateApplicationRequest(RpcRequest):

	def __init__(self):
		RpcRequest.__init__(self, 'Ims', '2017-04-30', 'CreateApplication','ims')

	def get_AppPrincipalName(self):
		return self.get_query_params().get('AppPrincipalName')

	def set_AppPrincipalName(self,AppPrincipalName):
		self.add_query_param('AppPrincipalName',AppPrincipalName)

	def get_SecretRequired(self):
		return self.get_query_params().get('SecretRequired')

	def set_SecretRequired(self,SecretRequired):
		self.add_query_param('SecretRequired',SecretRequired)

	def get_DisplayName(self):
		return self.get_query_params().get('DisplayName')

	def set_DisplayName(self,DisplayName):
		self.add_query_param('DisplayName',DisplayName)

	def get_AppType(self):
		return self.get_query_params().get('AppType')

	def set_AppType(self,AppType):
		self.add_query_param('AppType',AppType)

	def get_AccessTokenValidity(self):
		return self.get_query_params().get('AccessTokenValidity')

	def set_AccessTokenValidity(self,AccessTokenValidity):
		self.add_query_param('AccessTokenValidity',AccessTokenValidity)

	def get_PredefinedScopes(self):
		return self.get_query_params().get('PredefinedScopes')

	def set_PredefinedScopes(self,PredefinedScopes):
		self.add_query_param('PredefinedScopes',PredefinedScopes)

	def get_RefreshTokenValidity(self):
		return self.get_query_params().get('RefreshTokenValidity')

	def set_RefreshTokenValidity(self,RefreshTokenValidity):
		self.add_query_param('RefreshTokenValidity',RefreshTokenValidity)

	def get_RedirectUris(self):
		return self.get_query_params().get('RedirectUris')

	def set_RedirectUris(self,RedirectUris):
		self.add_query_param('RedirectUris',RedirectUris)