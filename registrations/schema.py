import graphene

# class InitiateOrder(graphene.Mutation):
#     class Arguments:
#         products = ProductsInput(required=True)
#         promocode = graphene.String(required=False)
#
#     Output = InitiateOrderObj
#
#     @login_required
#     def mutate(self, info, products, promocode=None):