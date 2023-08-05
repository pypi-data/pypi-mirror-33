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

class Trans(BaseObject):
    """
    
    """

    __config = {
        
        "62e74eea-3ac4-49ea-b02f-61b2210c2dc0" : OperationConfig("/labs/proxy/qkr2/internal/api2/trans", "create", ["X-Auth-Token"], []),
        
        "f288df84-2651-417c-819f-8e3842f5eb2d" : OperationConfig("/labs/proxy/qkr2/internal/api2/trans", "query", ["X-Auth-Token"], ["from","to"]),
        
        "de78b96f-154f-4aab-b884-93332efaf0f2" : OperationConfig("/labs/proxy/qkr2/internal/api2/trans/{id}", "read", ["X-Auth-Token"], []),
        
        "93fa211c-5433-4dbc-bd0f-cd14bc28e5ad" : OperationConfig("/labs/proxy/qkr2/internal/api2/trans/{id}", "update", ["X-Auth-Token"], []),
        
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
        Creates object of type Trans

        @param Dict mapObj, containing the required parameters to create a new object
        @return Trans of the response of created instance.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("62e74eea-3ac4-49ea-b02f-61b2210c2dc0", Trans(mapObj))











    @classmethod
    def query(cls,criteria):
        """
        Query objects of type Trans by id and optional criteria
        @param type criteria
        @return Trans object representing the response.
        @raise ApiException: raised an exception from the response status
        """

        return BaseObject.execute("f288df84-2651-417c-819f-8e3842f5eb2d", Trans(criteria))





    @classmethod
    def read(cls,id,criteria=None):
        """
        Returns objects of type Trans by id and optional criteria
        @param str id
        @param dict criteria
        @return instance of Trans
        @raise ApiException: raised an exception from the response status
        """
        mapObj =  RequestMap()
        if id:
            mapObj.set("id", id)

        if criteria:
            if (isinstance(criteria,RequestMap)):
                mapObj.setAll(criteria.getObject())
            else:
                mapObj.setAll(criteria)

        return BaseObject.execute("de78b96f-154f-4aab-b884-93332efaf0f2", Trans(mapObj))



    def update(self):
        """
        Updates an object of type Trans

        @return Trans object representing the response.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("93fa211c-5433-4dbc-bd0f-cd14bc28e5ad", self)






