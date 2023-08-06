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
from mastercardmastercom import ResourceConfig

class Retrievals(BaseObject):
    """
    
    """

    __config = {
        
        "624da83b-6db0-4e7a-9ae7-8ca4dd983791" : OperationConfig("/mastercom/v2/claims/{claim-id}/retrievalrequests/{request-id}/fulfillments", "create", [], []),
        
        "579bc51f-b612-4391-a8c7-eb0a5d0e23e9" : OperationConfig("/mastercom/v2/claims/{claim-id}/retrievalrequests", "create", [], []),
        
        "6807a2c6-ae22-432e-a7bb-3fb244979633" : OperationConfig("/mastercom/v2/claims/{claim-id}/retrievalrequests/loaddataforretrievalrequests", "query", [], []),
        
        "d03de493-2b1a-4cc9-88ef-c7855d0e1251" : OperationConfig("/mastercom/v2/claims/{claim-id}/retrievalrequests/{request-id}/documents", "query", [], ["format"]),
        
        "55710d34-8ff8-414d-8fef-43bbc769bfb9" : OperationConfig("/mastercom/v2/claims/{claim-id}/retrievalrequests/{request-id}/fulfillments/response", "create", [], []),
        
        "c8164396-47c1-411d-939b-b1b0ee96d81c" : OperationConfig("/mastercom/v2/retrievalrequests/status", "update", [], []),
        
    }

    def getOperationConfig(self,operationUUID):
        if operationUUID not in self.__config:
            raise Exception("Invalid operationUUID: "+operationUUID)

        return self.__config[operationUUID]

    def getOperationMetadata(self):
        return OperationMetadata(ResourceConfig.getInstance().getVersion(), ResourceConfig.getInstance().getHost(), ResourceConfig.getInstance().getContext(), ResourceConfig.getInstance().getJsonNative(), ResourceConfig.getInstance().getContentTypeOverride())


    @classmethod
    def acquirerFulfillARequest(cls,mapObj):
        """
        Creates object of type Retrievals

        @param Dict mapObj, containing the required parameters to create a new object
        @return Retrievals of the response of created instance.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("624da83b-6db0-4e7a-9ae7-8ca4dd983791", Retrievals(mapObj))






    @classmethod
    def create(cls,mapObj):
        """
        Creates object of type Retrievals

        @param Dict mapObj, containing the required parameters to create a new object
        @return Retrievals of the response of created instance.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("579bc51f-b612-4391-a8c7-eb0a5d0e23e9", Retrievals(mapObj))











    @classmethod
    def getPossibleValueListsForCreate(cls,criteria):
        """
        Query objects of type Retrievals by id and optional criteria
        @param type criteria
        @return Retrievals object representing the response.
        @raise ApiException: raised an exception from the response status
        """

        return BaseObject.execute("6807a2c6-ae22-432e-a7bb-3fb244979633", Retrievals(criteria))






    @classmethod
    def getDocumentation(cls,criteria):
        """
        Query objects of type Retrievals by id and optional criteria
        @param type criteria
        @return Retrievals object representing the response.
        @raise ApiException: raised an exception from the response status
        """

        return BaseObject.execute("d03de493-2b1a-4cc9-88ef-c7855d0e1251", Retrievals(criteria))

    @classmethod
    def issuerRespondToFulfillment(cls,mapObj):
        """
        Creates object of type Retrievals

        @param Dict mapObj, containing the required parameters to create a new object
        @return Retrievals of the response of created instance.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("55710d34-8ff8-414d-8fef-43bbc769bfb9", Retrievals(mapObj))







    def retrievalFullfilmentStatus(self):
        """
        Updates an object of type Retrievals

        @return Retrievals object representing the response.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("c8164396-47c1-411d-939b-b1b0ee96d81c", self)






