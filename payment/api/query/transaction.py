import graphene
from graphql_jwt.decorators import login_required

from access.models import UserAccess
from framework.api.helper import APIException
from payment.models import Transaction, Order
from payment.api.objects import TransactionStatusObj, TransactionObj, TransactionDetailObj


class TransactionFixObj(graphene.ObjectType):
    email = graphene.String()
    amount = graphene.Int()
    oldTransaction = graphene.Field(TransactionObj)
    newTransaction = graphene.Field(TransactionObj)


class ExcessPaymentObj(graphene.ObjectType):
    email = graphene.String()
    amount = graphene.Int()
    transactions = graphene.List(TransactionObj)


class Query(graphene.ObjectType):
    getTransactionDetail = graphene.Field(TransactionDetailObj, transactionID=graphene.String())
    getTransactionsApproved = graphene.List(TransactionDetailObj)
    getTransactionStatus = graphene.Field(TransactionStatusObj, transactionID=graphene.String())
    getTransactionList = graphene.List(TransactionObj)
    fixUnassociatedPayments = graphene.List(TransactionFixObj)
    listExcessPayments = graphene.List(ExcessPaymentObj)

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

    @login_required
    def resolve_fixUnassociatedPayments(self, info, **kwargs):
        user = info.context.user  # get request user
        if user.is_superuser:  # only super user is allowed to perform this action
            # find successful transactions that do not have a order associated
            trans = Transaction.objects.filter(
                isPaid=True,
                order__isnull=True
            )
            log = []  # for logging
            # for each of those transactions
            for t in trans:
                # try to find a matching order
                orders = Order.objects.filter(
                    # order should be the same user, of course!
                    user=t.user,
                    # trans associated should have same value in order to be replaced
                    transaction__amount=t.amount,
                    # existing associated trans should have failed in order to be replaced with the curr
                    transaction__isPaid=False,
                )
                # if a single fixable match is found
                if orders.count() == 1:
                    order = orders.first()
                    log.append({
                        "email": t.user.email,
                        "amount": t.amount,
                        "oldTransaction": order.transaction,
                        "newTransaction": t
                    })
                    # replace the failed transaction with the successful
                    order.transaction = t
                    order.save()  # save changes
                # TODO how to handle if multiple failed orders exist with same amount?
            return log
        raise APIException('You should be a super user to perform this action')

    @login_required
    def resolve_listExcessPayments(self, info, **kwargs):
        user = info.context.user
        if user.is_superuser:
            users = Transaction.objects.filter(
                isPaid=True,
                order__isnull=True
            ).values_list('user', flat=True).distinct()
            list = []
            for u in users:
                trans = Transaction.objects.filter(isPaid=True, user_id=u)
                if trans.values('amount').distinct().count() == 1:
                    data = {
                        "email": trans.first().user.email,
                        "amount": trans.first().amount,
                        "transactions": trans
                    }
                    list.append(data)
            return list
        else:
            raise APIException('You need to be a super-admin to do this.')