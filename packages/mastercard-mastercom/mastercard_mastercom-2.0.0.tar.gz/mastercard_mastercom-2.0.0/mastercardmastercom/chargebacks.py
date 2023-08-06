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

class Chargebacks(BaseObject):
    """
    
    """

    __config = {
        
        "ed920995-0ce4-4e4b-833b-1d8c4edf1b45" : OperationConfig("/mastercom/v2/chargebacks/acknowledge", "update", [], []),
        
        "057c0ba1-6980-405d-a465-3046d66b5e16" : OperationConfig("/mastercom/v2/claims/{claim-id}/chargebacks", "create", [], []),
        
        "29a76a88-cc3e-46d3-8de6-d0bf351679be" : OperationConfig("/mastercom/v2/claims/{claim-id}/chargebacks/{chargeback-id}/reversal", "create", [], []),
        
        "ff4eaf4e-2d49-4d22-9e7b-64f77dcd3911" : OperationConfig("/mastercom/v2/claims/{claim-id}/chargebacks/{chargeback-id}/documents", "query", [], ["format"]),
        
        "7b4174bd-442d-47b4-90be-9d5aabc98535" : OperationConfig("/mastercom/v2/claims/{claim-id}/chargebacks/loaddataforchargebacks", "query", [], ["chargeback-type"]),
        
        "38947c90-b485-4d1a-a4fc-4054f4fdef6b" : OperationConfig("/mastercom/v2/chargebacks/status", "update", [], []),
        
        "ac038b53-b3ae-413c-9a51-6ebf777f0927" : OperationConfig("/mastercom/v2/claims/{claim-id}/chargebacks/{chargeback-id}", "update", [], []),
        
    }

    def getOperationConfig(self,operationUUID):
        if operationUUID not in self.__config:
            raise Exception("Invalid operationUUID: "+operationUUID)

        return self.__config[operationUUID]

    def getOperationMetadata(self):
        return OperationMetadata(ResourceConfig.getInstance().getVersion(), ResourceConfig.getInstance().getHost(), ResourceConfig.getInstance().getContext(), ResourceConfig.getInstance().getJsonNative(), ResourceConfig.getInstance().getContentTypeOverride())



    def acknowledgeReceivedChargebacks(self):
        """
        Updates an object of type Chargebacks

        @return Chargebacks object representing the response.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("ed920995-0ce4-4e4b-833b-1d8c4edf1b45", self)





    @classmethod
    def create(cls,mapObj):
        """
        Creates object of type Chargebacks

        @param Dict mapObj, containing the required parameters to create a new object
        @return Chargebacks of the response of created instance.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("057c0ba1-6980-405d-a465-3046d66b5e16", Chargebacks(mapObj))






    @classmethod
    def createReversal(cls,mapObj):
        """
        Creates object of type Chargebacks

        @param Dict mapObj, containing the required parameters to create a new object
        @return Chargebacks of the response of created instance.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("29a76a88-cc3e-46d3-8de6-d0bf351679be", Chargebacks(mapObj))











    @classmethod
    def retrieveDocumentation(cls,criteria):
        """
        Query objects of type Chargebacks by id and optional criteria
        @param type criteria
        @return Chargebacks object representing the response.
        @raise ApiException: raised an exception from the response status
        """

        return BaseObject.execute("ff4eaf4e-2d49-4d22-9e7b-64f77dcd3911", Chargebacks(criteria))






    @classmethod
    def getPossibleValueListsForCreate(cls,criteria):
        """
        Query objects of type Chargebacks by id and optional criteria
        @param type criteria
        @return Chargebacks object representing the response.
        @raise ApiException: raised an exception from the response status
        """

        return BaseObject.execute("7b4174bd-442d-47b4-90be-9d5aabc98535", Chargebacks(criteria))


    def chargebacksStatus(self):
        """
        Updates an object of type Chargebacks

        @return Chargebacks object representing the response.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("38947c90-b485-4d1a-a4fc-4054f4fdef6b", self)






    def update(self):
        """
        Updates an object of type Chargebacks

        @return Chargebacks object representing the response.
        @raise ApiException: raised an exception from the response status
        """
        return BaseObject.execute("ac038b53-b3ae-413c-9a51-6ebf777f0927", self)






