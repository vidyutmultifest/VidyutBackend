import graphene
import requests
import json

from graphql_jwt.decorators import login_required

from framework.api.helper import APIException
from payment.acrd.helper import getTransactionPayload, decryptPayload
from framework.settings import ACRD_ENDPOINT

from payment.models import Transaction


class PaymentLinkObj(graphene.ObjectType):
    url = graphene.String()
    data = graphene.String()
    code = graphene.String()


class PaymentStatusObj(graphene.ObjectType):
    status = graphene.Boolean()
    data = graphene.JSONString()


class Query(object):
    getPaymentGatewayData = graphene.Field(PaymentLinkObj, transactionID=graphene.String())
    getOnlinePaymentStatus = graphene.Field(PaymentStatusObj, transactionID=graphene.String())
    refetchPendingStatus = graphene.Boolean()

    @login_required
    def resolve_refetchPendingStatus(self, info, **kwargs):
        pt = Transaction.objects.filter(isOnline=True, isProcessed=False)
        for t in pt:
            payload = getTransactionPayload(t.amount, t.transactionID)
            print(payload)
            f = requests.post(ACRD_ENDPOINT + '/doubleverifythirdparty', data=payload)
            print(f.status_code)
            try:
                k = f.json()
                # Decrypt Response Data from ACRD, receives a JSON
                data = decryptPayload(k["data"])
                print(data)

                if k["response"]:
                    try:
                        jsonData = json.loads(data)
                        t.isPaid = jsonData['status'] == "SUCCESS"
                        t.isProcessed = True
                        t.manualIssue = False
                        t.transactionData = data
                        t.save()
                    except Exception as e:
                        t.isPaid = False
                        t.isProcessed = True
                        t.manualIssue = False
                        t.transactionData = data
                        t.save()
            except Exception as e:
                print('hello')
                print(f.text)
                t.isPaid = False
                t.isProcessed = True
                t.manualIssue = False
                t.transactionData = f.text
                t.save()

        return True

    @login_required
    def resolve_getPaymentGatewayData(self, info, **kwargs):
        transactionID = kwargs.get('transactionID')
        try:
            tobj = Transaction.objects.get(transactionID=transactionID)
        except Transaction.DoesNotExist:
            raise APIException("Transaction not found in the database.")
        payload = getTransactionPayload(tobj.amount, transactionID)
        return PaymentLinkObj(
            data=payload['encdata'],
            code=payload['code'],
            url=ACRD_ENDPOINT + '/makethirdpartypayment'
        )

    @login_required
    def resolve_getOnlinePaymentStatus(self, info, **kwargs):
        transactionID = kwargs.get('transactionID')
        try:
            tobj = Transaction.objects.get(transactionID=transactionID)
        except Transaction.DoesNotExist:
            raise APIException("Transaction not found in the database.")

        payload = getTransactionPayload(tobj.amount, transactionID)
        try:
            f = requests.post(ACRD_ENDPOINT + '/doubleverifythirdparty', data=payload)
            k = f.json()
        # TODO : Do better error handling
        except Exception as e:
            return PaymentStatusObj(status=False, data='Failed')

        # Decrypt Response Data from ACRD, receives a JSON
        data = decryptPayload(k["data"])

        if k["response"]:
            jsonData = json.loads(data)
            tobj.isPaid = jsonData['status'] == "SUCCESS"
            tobj.isProcessed = True
            tobj.manualIssue = False
            tobj.transactionData = data
            tobj.save()
        return PaymentStatusObj(status=k["response"], data=data)
