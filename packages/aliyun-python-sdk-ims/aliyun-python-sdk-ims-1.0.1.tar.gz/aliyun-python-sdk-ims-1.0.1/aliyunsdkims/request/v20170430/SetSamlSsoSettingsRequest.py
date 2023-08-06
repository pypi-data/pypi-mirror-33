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
class SetSamlSsoSettingsRequest(RpcRequest):

	def __init__(self):
		RpcRequest.__init__(self, 'Ims', '2017-04-30', 'SetSamlSsoSettings','ims')

	def get_MetadataDocument(self):
		return self.get_query_params().get('MetadataDocument')

	def set_MetadataDocument(self,MetadataDocument):
		self.add_query_param('MetadataDocument',MetadataDocument)

	def get_UseTenantSpecificSp(self):
		return self.get_query_params().get('UseTenantSpecificSp')

	def set_UseTenantSpecificSp(self,UseTenantSpecificSp):
		self.add_query_param('UseTenantSpecificSp',UseTenantSpecificSp)

	def get_SsoEnabled(self):
		return self.get_query_params().get('SsoEnabled')

	def set_SsoEnabled(self,SsoEnabled):
		self.add_query_param('SsoEnabled',SsoEnabled)