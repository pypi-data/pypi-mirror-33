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

class Airport(BaseObject):
    """
    
    """

    __config = {
        
        "006a941f-45ba-4cdc-879f-d67dff24ff43" : OperationConfig("/loyalty/v1/airport/lounges", "query", ["x-client-correlation-id"], ["searchText","preferredLanguage"]),
        
        "757e47ba-3e93-466f-b141-f5eab5ffa64a" : OperationConfig("/loyalty/v1/airport/lounges/{loungeId}/detail", "query", ["x-client-correlation-id"], ["preferredLanguage"]),
        
        "ba018710-06f3-4961-a99b-636bccdbf66b" : OperationConfig("/loyalty/v1/airport/lounges/{loungeId}/history", "query", ["x-client-correlation-id"], ["userId"]),
        
        "105ecd92-fc18-47be-9312-beb39b21bdf9" : OperationConfig("/loyalty/v1/airport/{userId}/dmc", "query", ["x-client-correlation-id"], []),
        
        "e12a345e-b53a-4092-9c9c-eab53b5fc730" : OperationConfig("/loyalty/v1/users/{userId}/airport", "query", ["x-client-correlation-id"], []),
        
    }

    def getOperationConfig(self,operationUUID):
        if operationUUID not in self.__config:
            raise Exception("Invalid operationUUID: "+operationUUID)

        return self.__config[operationUUID]

    def getOperationMetadata(self):
        return OperationMetadata(ResourceConfig.getInstance().getVersion(), ResourceConfig.getInstance().getHost(), ResourceConfig.getInstance().getContext(), ResourceConfig.getInstance().getJsonNative(), ResourceConfig.getInstance().getContentTypeOverride())







    @classmethod
    def getLounges(cls,criteria):
        """
        Query objects of type Airport by id and optional criteria
        @param type criteria
        @return Airport object representing the response.
        @raise ApiException: raised an exception from the response status
        """

        return BaseObject.execute("006a941f-45ba-4cdc-879f-d67dff24ff43", Airport(criteria))






    @classmethod
    def getLoungeDetail(cls,criteria):
        """
        Query objects of type Airport by id and optional criteria
        @param type criteria
        @return Airport object representing the response.
        @raise ApiException: raised an exception from the response status
        """

        return BaseObject.execute("757e47ba-3e93-466f-b141-f5eab5ffa64a", Airport(criteria))






    @classmethod
    def getLoungeHistory(cls,criteria):
        """
        Query objects of type Airport by id and optional criteria
        @param type criteria
        @return Airport object representing the response.
        @raise ApiException: raised an exception from the response status
        """

        return BaseObject.execute("ba018710-06f3-4961-a99b-636bccdbf66b", Airport(criteria))






    @classmethod
    def getDMC(cls,criteria):
        """
        Query objects of type Airport by id and optional criteria
        @param type criteria
        @return Airport object representing the response.
        @raise ApiException: raised an exception from the response status
        """

        return BaseObject.execute("105ecd92-fc18-47be-9312-beb39b21bdf9", Airport(criteria))






    @classmethod
    def userAirportRegistrationStatus(cls,criteria):
        """
        Query objects of type Airport by id and optional criteria
        @param type criteria
        @return Airport object representing the response.
        @raise ApiException: raised an exception from the response status
        """

        return BaseObject.execute("e12a345e-b53a-4092-9c9c-eab53b5fc730", Airport(criteria))


