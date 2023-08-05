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

class Card(BaseObject):
    """
    
    """

    __config = {
        
        "b15de0f9-7a95-4c36-9e09-2de3ec300da0" : OperationConfig("/labs/proxy/qkr2/internal/api2/card", "create", ["X-Auth-Token"], []),
        
        "a39958c6-e397-41d5-9c67-4d10782f598b" : OperationConfig("/labs/proxy/qkr2/internal/api2/card/{id}", "delete", ["X-Auth-Token"], []),
        
        "65f08e67-ef2d-4565-8aba-9c06bac9cec2" : OperationConfig("/labs/proxy/qkr2/internal/api2/card", "query", ["X-Auth-Token"], []),
        
        "fc30a39a-efc4-48fe-b7f7-68dd334fe35f" : OperationConfig("/labs/proxy/qkr2/internal/api2/card/{id}", "read", ["X-Auth-Token"], []),
        
        "bf752d4b-28e1-43a6-909b-11423367415c" : OperationConfig("/labs/proxy/qkr2/internal/api2/card/{id}", "update", ["X-Auth-Token"], []),
        
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
        Creates object of type Card

        @param Dict mapObj, containing the required parameters to create a new object
        @return Card of the response of created instance.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("b15de0f9-7a95-4c36-9e09-2de3ec300da0", Card(mapObj))









    @classmethod
    def deleteById(cls,id,map=None):
        """
        Delete object of type Card by id

        @param str id
        @return Card of the response of the deleted instance.
        @raise ApiException: raised an exception from the response status
        """

        mapObj =  RequestMap()
        if id:
            mapObj.set("id", id)

        if map:
            if (isinstance(map,RequestMap)):
                mapObj.setAll(map.getObject())
            else:
                mapObj.setAll(map)

        return BaseObject.execute("a39958c6-e397-41d5-9c67-4d10782f598b", Card(mapObj))

    def delete(self):
        """
        Delete object of type Card

        @return Card of the response of the deleted instance.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("a39958c6-e397-41d5-9c67-4d10782f598b", self)








    @classmethod
    def query(cls,criteria):
        """
        Query objects of type Card by id and optional criteria
        @param type criteria
        @return Card object representing the response.
        @raise ApiException: raised an exception from the response status
        """

        return BaseObject.execute("65f08e67-ef2d-4565-8aba-9c06bac9cec2", Card(criteria))





    @classmethod
    def read(cls,id,criteria=None):
        """
        Returns objects of type Card by id and optional criteria
        @param str id
        @param dict criteria
        @return instance of Card
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

        return BaseObject.execute("fc30a39a-efc4-48fe-b7f7-68dd334fe35f", Card(mapObj))



    def update(self):
        """
        Updates an object of type Card

        @return Card object representing the response.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("bf752d4b-28e1-43a6-909b-11423367415c", self)






