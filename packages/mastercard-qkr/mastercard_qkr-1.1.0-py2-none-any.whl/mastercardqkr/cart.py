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

class Cart(BaseObject):
    """
    
    """

    __config = {
        
        "fd703bc2-7932-4208-bef5-ac20640ee36d" : OperationConfig("/labs/proxy/qkr2/internal/api2/cart/{id}", "delete", ["X-Auth-Token"], []),
        
        "cba23570-9de3-4cfd-b2fa-6e87e2b08251" : OperationConfig("/labs/proxy/qkr2/internal/api2/cart", "query", ["X-Auth-Token"], []),
        
        "683e6c04-4c4d-4d27-9b64-2cf3edcb5cbd" : OperationConfig("/labs/proxy/qkr2/internal/api2/cart/{id}", "read", ["X-Auth-Token"], []),
        
    }

    def getOperationConfig(self,operationUUID):
        if operationUUID not in self.__config:
            raise Exception("Invalid operationUUID: "+operationUUID)

        return self.__config[operationUUID]

    def getOperationMetadata(self):
        return OperationMetadata(ResourceConfig.getInstance().getVersion(), ResourceConfig.getInstance().getHost(), ResourceConfig.getInstance().getContext(), ResourceConfig.getInstance().getJsonNative(), ResourceConfig.getInstance().getContentTypeOverride())





    @classmethod
    def deleteById(cls,id,map=None):
        """
        Delete object of type Cart by id

        @param str id
        @return Cart of the response of the deleted instance.
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

        return BaseObject.execute("fd703bc2-7932-4208-bef5-ac20640ee36d", Cart(mapObj))

    def delete(self):
        """
        Delete object of type Cart

        @return Cart of the response of the deleted instance.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("fd703bc2-7932-4208-bef5-ac20640ee36d", self)








    @classmethod
    def query(cls,criteria):
        """
        Query objects of type Cart by id and optional criteria
        @param type criteria
        @return Cart object representing the response.
        @raise ApiException: raised an exception from the response status
        """

        return BaseObject.execute("cba23570-9de3-4cfd-b2fa-6e87e2b08251", Cart(criteria))





    @classmethod
    def read(cls,id,criteria=None):
        """
        Returns objects of type Cart by id and optional criteria
        @param str id
        @param dict criteria
        @return instance of Cart
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

        return BaseObject.execute("683e6c04-4c4d-4d27-9b64-2cf3edcb5cbd", Cart(mapObj))



