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

class Benefits(BaseObject):
    """
    
    """

    __config = {
        
        "3a50f5fe-08da-49e7-bafe-d12e9dee3133" : OperationConfig("/loyalty/v1/benefits/assigned", "query", ["x-client-correlation-id"], ["ica","userId","channel","preferredLanguage"]),
        
        "ee63e324-9e18-4589-b21c-9298f1093c7b" : OperationConfig("/loyalty/v1/benefits/{benefitId}/detail", "query", ["x-client-correlation-id"], ["ica","channel","preferredLanguage"]),
        
        "eba18ea5-13c2-4049-ab34-72c0fd3e7e48" : OperationConfig("/loyalty/v1/benefits", "query", ["x-client-correlation-id"], ["ica","cardProductType","channel","preferredLanguage"]),
        
        "33baf66f-73a4-48a6-a221-436eaf00d910" : OperationConfig("/loyalty/v1/benefits", "create", ["x-client-correlation-id"], []),
        
        "3638eacb-8733-477d-971e-e0c89a1ae489" : OperationConfig("/loyalty/v1/benefits/programterms", "query", ["x-client-correlation-id"], ["ica","preferredLanguage"]),
        
        "8eec1d4f-0916-4349-9027-cb93ac6395c2" : OperationConfig("/loyalty/v1/users/{userId}/benefits", "query", ["x-client-correlation-id"], []),
        
    }

    def getOperationConfig(self,operationUUID):
        if operationUUID not in self.__config:
            raise Exception("Invalid operationUUID: "+operationUUID)

        return self.__config[operationUUID]

    def getOperationMetadata(self):
        return OperationMetadata(ResourceConfig.getInstance().getVersion(), ResourceConfig.getInstance().getHost(), ResourceConfig.getInstance().getContext(), ResourceConfig.getInstance().getJsonNative(), ResourceConfig.getInstance().getContentTypeOverride())







    @classmethod
    def getAssignedBenefits(cls,criteria):
        """
        Query objects of type Benefits by id and optional criteria
        @param type criteria
        @return Benefits object representing the response.
        @raise ApiException: raised an exception from the response status
        """

        return BaseObject.execute("3a50f5fe-08da-49e7-bafe-d12e9dee3133", Benefits(criteria))






    @classmethod
    def getBenefitDetail(cls,criteria):
        """
        Query objects of type Benefits by id and optional criteria
        @param type criteria
        @return Benefits object representing the response.
        @raise ApiException: raised an exception from the response status
        """

        return BaseObject.execute("ee63e324-9e18-4589-b21c-9298f1093c7b", Benefits(criteria))






    @classmethod
    def getBenefits(cls,criteria):
        """
        Query objects of type Benefits by id and optional criteria
        @param type criteria
        @return Benefits object representing the response.
        @raise ApiException: raised an exception from the response status
        """

        return BaseObject.execute("eba18ea5-13c2-4049-ab34-72c0fd3e7e48", Benefits(criteria))

    @classmethod
    def selectBenefits(cls,mapObj):
        """
        Creates object of type Benefits

        @param Dict mapObj, containing the required parameters to create a new object
        @return Benefits of the response of created instance.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("33baf66f-73a4-48a6-a221-436eaf00d910", Benefits(mapObj))











    @classmethod
    def getProgramTerms(cls,criteria):
        """
        Query objects of type Benefits by id and optional criteria
        @param type criteria
        @return Benefits object representing the response.
        @raise ApiException: raised an exception from the response status
        """

        return BaseObject.execute("3638eacb-8733-477d-971e-e0c89a1ae489", Benefits(criteria))






    @classmethod
    def userBenefitsRegistrationStatus(cls,criteria):
        """
        Query objects of type Benefits by id and optional criteria
        @param type criteria
        @return Benefits object representing the response.
        @raise ApiException: raised an exception from the response status
        """

        return BaseObject.execute("8eec1d4f-0916-4349-9027-cb93ac6395c2", Benefits(criteria))


