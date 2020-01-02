import graphene
from graphql_jwt.decorators import login_required

from access.models import UserAccess
from framework.api.helper import APIException
from payment.models import Transaction
from payment.api.objects import TransactionStatusObj, TransactionObj, TransactionDetailObj


class Query(graphene.ObjectType):
    getTransactionDetail = graphene.Field(TransactionDetailObj, transactionID=graphene.String())
    getTransactionsApproved = graphene.List(TransactionDetailObj)
    getTransactionStatus = graphene.Field(TransactionStatusObj, transactionID=graphene.String())
    getTransactionList = graphene.List(TransactionObj)

    @login_required
    def resolve_getTransactionDetail(self, info, **kwargs):
        transactionID = kwargs.get('transactionID')
        user = info.context.user
        try:
            tobj = Transaction.objects.get(transactionID=transactionID)

            # a superuser can always see the transaction
            if user.is_superuser:
                return tobj

            # an user can view details of his own transaction
            if user == tobj.user:
                return tobj

            # check user's access based on UserAccess Model
            try:
                access = UserAccess.objects.get(user=user)
                if access.canAcceptPayment or access.viewAllTransactions:

                    # TODO: CRITICAL! if its not viewed at counter, but elsewhere, it shouldn't modify the transaction
                    # Modify transaction if it was viewed at the counter
                    if tobj.isPaid is False:  # no modification required if already paid
                        tobj.issuer = user
                        tobj.isPending = True
                        tobj.isProcessed = False
                        tobj.save()

                    return tobj
                else:
                    raise APIException("Access level set for you is not enough to perform this query.")
            except UserAccess.DoesNotExist:
                raise APIException("You are not permitted to view the details of this transactions.")
        except Transaction.DoesNotExist:
            raise APIException("Transaction not found in the database.")

    # TODO: API name confuses
    @login_required
    def resolve_getTransactionsApproved(self, info, **kwargs):
        user = info.context.user
        try:
            if UserAccess.objects.get(user=user).canAcceptPayment:
                return Transaction.objects.values().filter(issuer=user, isPaid=True)
            else:
                raise APIException(
                    "This API is for volunteer's who can collect payment. You don't have permission to view this."
                )
        except UserAccess.DoesNotExist:
            raise APIException("You don't have access to view this.")

    @login_required
    def resolve_getTransactionStatus(self, info, **kwargs):
        user = info.context.user
        transactionID = kwargs.get('transactionID')
        try:
            tobj = Transaction.objects.get(transactionID=transactionID)

            # a superuser can always see transaction status of any transaction
            if user.is_superuser:
                return tobj

            # an user can always view the status of his own transaction
            if tobj.user == user:
                return tobj

            try:
                access = UserAccess.objects.get(user=user)
                if access.canAcceptPayment or access.viewAllTransactions:
                    return tobj
                else:
                    raise APIException("You dont have the access enabled to view the status of this transaction.")
            except UserAccess.DoesNotExist:
                raise APIException("You are not allowed to view the status of this transaction.")
        except Transaction.DoesNotExist:
            raise APIException("Transaction with the given transactionID does not exist")

    # TODO: Add support for queries like isPaid, product, username/vid etc.
    @login_required
    def resolve_getTransactionList(self, info, **kwargs):
        user = info.context.user
        transactions = Transaction.objects.values().all().order_by('-timestamp')
        if user.is_superuser:
            return transactions
        try:
            if UserAccess.objects.get(user=user).viewAllTransactions:
                return transactions
            else:
                raise APIException(
                    "Access denied: You dont have the access enabled to view details of all transactions."
                )
        except UserAccess.DoesNotExist:
            raise APIException("Access denied: You are not allowed view all transactions.")

