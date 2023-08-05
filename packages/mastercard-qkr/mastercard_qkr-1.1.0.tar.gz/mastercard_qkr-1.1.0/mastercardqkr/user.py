#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (c) 2016 MasterCard International Incorporated
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are
# permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this list of
# conditions and the following disclaimer.
# Redistributions in binary form must reproduce the above copyright notice, this list of
# conditions and the following disclaimer in the documentation and/or other materials
# provided with the distribution.
# Neither the name of the MasterCard International Incorporated nor the names of its
# contributors may be used to endorse or promote products derived from this software
# without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
# SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#


from __future__ import absolute_import
from mastercardapicore import BaseObject
from mastercardapicore import RequestMap
from mastercardapicore import OperationConfig
from mastercardapicore import OperationMetadata
from mastercardqkr import ResourceConfig

class User(BaseObject):
    """
    
    """

    __config = {
        
        "5fa3a3fc-36aa-4e3b-bf38-affcf5e517d0" : OperationConfig("/labs/proxy/qkr2/internal/api2/user", "create", ["X-Auth-Token"], []),
        
        "3f0e5566-d304-41dc-a65c-738cc0c95922" : OperationConfig("/labs/proxy/qkr2/internal/api2/user", "query", ["X-Auth-Token"], []),
        
        "e7d55e01-fdb6-4bb2-be8b-e91bd70fa39e" : OperationConfig("/labs/proxy/qkr2/internal/api2/user", "update", ["X-Auth-Token"], []),
        
    }

    def getOperationConfig(self,operationUUID):
        if operationUUID not in self.__config:
            raise Exception("Invalid operationUUID: "+operationUUID)

        return self.__config[operationUUID]

    def getOperationMetadata(self):
        return OperationMetadata(ResourceConfig.getInstance().getVersion(), ResourceConfig.getInstance().getHost(), ResourceConfig.getInstance().getContext(), ResourceConfig.getInstance().getJsonNative(), ResourceConfig.getInstance().getContentTypeOverride())


    @classmethod
    def create(cls,mapObj):
        """
        Creates object of type User

        @param Dict mapObj, containing the required parameters to create a new object
        @return User of the response of created instance.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("5fa3a3fc-36aa-4e3b-bf38-affcf5e517d0", User(mapObj))











    @classmethod
    def query(cls,criteria):
        """
        Query objects of type User by id and optional criteria
        @param type criteria
        @return User object representing the response.
        @raise ApiException: raised an exception from the response status
        """

        return BaseObject.execute("3f0e5566-d304-41dc-a65c-738cc0c95922", User(criteria))


    def update(self):
        """
        Updates an object of type User

        @return User object representing the response.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("e7d55e01-fdb6-4bb2-be8b-e91bd70fa39e", self)






