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

class Offers(BaseObject):
    """
    
    """

    __config = {
        
        "82f1d3cd-852a-4220-b177-c772b710da77" : OperationConfig("/loyalty/v1/offers", "query", ["x-client-correlation-id"], ["userId","preferredLanguage","sort","category","featured","favorite","partner","latitude","longitude","searchRadius"]),
        
        "80e0bc8c-598a-4b1d-a9cd-5512c8c298e5" : OperationConfig("/loyalty/v1/offers/{offerId}/activate", "create", ["x-client-correlation-id"], []),
        
        "54b65034-e519-44fc-bfdc-feb17dd1608c" : OperationConfig("/loyalty/v1/offers/{offerId}/detail", "query", ["x-client-correlation-id"], ["userId","preferredLanguage"]),
        
        "504c6c24-a75b-422a-9161-7476550a4d08" : OperationConfig("/loyalty/v1/offers/{offerId}/favorite", "create", ["x-client-correlation-id"], []),
        
        "cd951f58-229f-4a50-8cfb-51b32eb00705" : OperationConfig("/loyalty/v1/offers/{offerId}/redeem", "create", ["x-client-correlation-id"], []),
        
        "0b56f272-2d00-4367-81fe-2a293738fef1" : OperationConfig("/loyalty/v1/offers/{offerId}/unfavorite", "create", ["x-client-correlation-id"], []),
        
        "ae48ab02-9426-4855-bcbe-c5df48f0fe47" : OperationConfig("/loyalty/v1/offers/promo", "create", ["x-client-correlation-id"], []),
        
        "af2f8650-c254-43d0-abd0-c44085273bb2" : OperationConfig("/loyalty/v1/offers/redeemed", "query", ["x-client-correlation-id"], ["userId","preferredLanguage"]),
        
        "76e2b9e7-c923-4ba2-89db-ddb03efb3158" : OperationConfig("/loyalty/v1/points/expiring", "query", ["x-client-correlation-id"], ["userId"]),
        
        "9a298410-3a3b-47ee-94eb-55f954d66a45" : OperationConfig("/loyalty/v1/points", "query", ["x-client-correlation-id"], ["userId"]),
        
        "6e31f6e7-0869-4faa-8256-dafb857c948a" : OperationConfig("/loyalty/v1/users/{userId}/offers", "query", ["x-client-correlation-id"], []),
        
        "53c20376-9ced-48ef-9a41-5f1c5321f2cb" : OperationConfig("/loyalty/v1/vouchers", "query", ["x-client-correlation-id"], ["userId"]),
        
        "63a2be4d-0652-489f-b4d4-405ef19fcf17" : OperationConfig("/loyalty/v1/vouchers/{voucherId}/detail", "query", ["x-client-correlation-id"], ["userId"]),
        
    }

    def getOperationConfig(self,operationUUID):
        if operationUUID not in self.__config:
            raise Exception("Invalid operationUUID: "+operationUUID)

        return self.__config[operationUUID]

    def getOperationMetadata(self):
        return OperationMetadata(ResourceConfig.getInstance().getVersion(), ResourceConfig.getInstance().getHost(), ResourceConfig.getInstance().getContext(), ResourceConfig.getInstance().getJsonNative(), ResourceConfig.getInstance().getContentTypeOverride())







    @classmethod
    def getOffers(cls,criteria):
        """
        Query objects of type Offers by id and optional criteria
        @param type criteria
        @return Offers object representing the response.
        @raise ApiException: raised an exception from the response status
        """

        return BaseObject.execute("82f1d3cd-852a-4220-b177-c772b710da77", Offers(criteria))

    @classmethod
    def activateOffer(cls,mapObj):
        """
        Creates object of type Offers

        @param Dict mapObj, containing the required parameters to create a new object
        @return Offers of the response of created instance.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("80e0bc8c-598a-4b1d-a9cd-5512c8c298e5", Offers(mapObj))











    @classmethod
    def getOfferDetail(cls,criteria):
        """
        Query objects of type Offers by id and optional criteria
        @param type criteria
        @return Offers object representing the response.
        @raise ApiException: raised an exception from the response status
        """

        return BaseObject.execute("54b65034-e519-44fc-bfdc-feb17dd1608c", Offers(criteria))

    @classmethod
    def favoriteOffer(cls,mapObj):
        """
        Creates object of type Offers

        @param Dict mapObj, containing the required parameters to create a new object
        @return Offers of the response of created instance.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("504c6c24-a75b-422a-9161-7476550a4d08", Offers(mapObj))






    @classmethod
    def redeemOffer(cls,mapObj):
        """
        Creates object of type Offers

        @param Dict mapObj, containing the required parameters to create a new object
        @return Offers of the response of created instance.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("cd951f58-229f-4a50-8cfb-51b32eb00705", Offers(mapObj))






    @classmethod
    def unfavoriteOffer(cls,mapObj):
        """
        Creates object of type Offers

        @param Dict mapObj, containing the required parameters to create a new object
        @return Offers of the response of created instance.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("0b56f272-2d00-4367-81fe-2a293738fef1", Offers(mapObj))






    @classmethod
    def submitOfferPromo(cls,mapObj):
        """
        Creates object of type Offers

        @param Dict mapObj, containing the required parameters to create a new object
        @return Offers of the response of created instance.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("ae48ab02-9426-4855-bcbe-c5df48f0fe47", Offers(mapObj))











    @classmethod
    def getRedeemedOffers(cls,criteria):
        """
        Query objects of type Offers by id and optional criteria
        @param type criteria
        @return Offers object representing the response.
        @raise ApiException: raised an exception from the response status
        """

        return BaseObject.execute("af2f8650-c254-43d0-abd0-c44085273bb2", Offers(criteria))






    @classmethod
    def getPointsExpiring(cls,criteria):
        """
        Query objects of type Offers by id and optional criteria
        @param type criteria
        @return Offers object representing the response.
        @raise ApiException: raised an exception from the response status
        """

        return BaseObject.execute("76e2b9e7-c923-4ba2-89db-ddb03efb3158", Offers(criteria))






    @classmethod
    def getPoints(cls,criteria):
        """
        Query objects of type Offers by id and optional criteria
        @param type criteria
        @return Offers object representing the response.
        @raise ApiException: raised an exception from the response status
        """

        return BaseObject.execute("9a298410-3a3b-47ee-94eb-55f954d66a45", Offers(criteria))






    @classmethod
    def userOffersRegistrationStatus(cls,criteria):
        """
        Query objects of type Offers by id and optional criteria
        @param type criteria
        @return Offers object representing the response.
        @raise ApiException: raised an exception from the response status
        """

        return BaseObject.execute("6e31f6e7-0869-4faa-8256-dafb857c948a", Offers(criteria))






    @classmethod
    def getVouchers(cls,criteria):
        """
        Query objects of type Offers by id and optional criteria
        @param type criteria
        @return Offers object representing the response.
        @raise ApiException: raised an exception from the response status
        """

        return BaseObject.execute("53c20376-9ced-48ef-9a41-5f1c5321f2cb", Offers(criteria))






    @classmethod
    def getVoucherDetail(cls,criteria):
        """
        Query objects of type Offers by id and optional criteria
        @param type criteria
        @return Offers object representing the response.
        @raise ApiException: raised an exception from the response status
        """

        return BaseObject.execute("63a2be4d-0652-489f-b4d4-405ef19fcf17", Offers(criteria))


