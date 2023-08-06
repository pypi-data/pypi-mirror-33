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
from mastercardmcon import ResourceConfig

class User(BaseObject):
    """
    
    """

    __config = {
        
        "cb1c860d-7866-40b2-bb31-7423c0e87030" : OperationConfig("/bundle/profile/v1/users", "create", ["x-client-correlation-id"], []),
        
        "821d367c-f3c1-41af-bb8b-a3213c0d00c3" : OperationConfig("/bundle/profile/v1/users/{userId}", "delete", ["x-client-correlation-id"], []),
        
        "0d2a22fc-5815-4162-9a6f-e395eb734433" : OperationConfig("/bundle/profile/v1/users/{userId}/patch", "create", ["x-client-correlation-id"], []),
        
        "c809b61c-52cc-44db-9b9e-48b17d01a900" : OperationConfig("/bundle/profile/v1/users/{userId}", "read", ["x-client-correlation-id"], []),
        
        "eb9d710c-153e-4b7b-b9e9-1a4c5017dd9c" : OperationConfig("/bundle/profile/v1/users/{userId}", "update", ["x-client-correlation-id"], []),
        
    }

    def getOperationConfig(self,operationUUID):
        if operationUUID not in self.__config:
            raise Exception("Invalid operationUUID: "+operationUUID)

        return self.__config[operationUUID]

    def getOperationMetadata(self):
        return OperationMetadata(ResourceConfig.getInstance().getVersion(), ResourceConfig.getInstance().getHost(), ResourceConfig.getInstance().getContext(), ResourceConfig.getInstance().getJsonNative(), ResourceConfig.getInstance().getContentTypeOverride())


    @classmethod
    def createUser(cls,mapObj):
        """
        Creates object of type User

        @param Dict mapObj, containing the required parameters to create a new object
        @return User of the response of created instance.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("cb1c860d-7866-40b2-bb31-7423c0e87030", User(mapObj))









    @classmethod
    def deleteUserById(cls,id,map=None):
        """
        Delete object of type User by id

        @param str id
        @return User of the response of the deleted instance.
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

        return BaseObject.execute("821d367c-f3c1-41af-bb8b-a3213c0d00c3", User(mapObj))

    def deleteUser(self):
        """
        Delete object of type User

        @return User of the response of the deleted instance.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("821d367c-f3c1-41af-bb8b-a3213c0d00c3", self)



    @classmethod
    def patchUser(cls,mapObj):
        """
        Creates object of type User

        @param Dict mapObj, containing the required parameters to create a new object
        @return User of the response of created instance.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("0d2a22fc-5815-4162-9a6f-e395eb734433", User(mapObj))










    @classmethod
    def readUser(cls,id,criteria=None):
        """
        Returns objects of type User by id and optional criteria
        @param str id
        @param dict criteria
        @return instance of User
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

        return BaseObject.execute("c809b61c-52cc-44db-9b9e-48b17d01a900", User(mapObj))



    def updateUser(self):
        """
        Updates an object of type User

        @return User object representing the response.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("eb9d710c-153e-4b7b-b9e9-1a4c5017dd9c", self)






