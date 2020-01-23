import csv

import graphene
from django.db.models import Count
from graphql_jwt.decorators import login_required

from participants.models import Profile, College
from payment.models import Order
from products.models import Product


class branchWiseStatObj(graphene.ObjectType):
    name = graphene.String()
    count = graphene.Int()

    def resolve_name(self, info):
        return self['branch']

    def resolve_count(self, info):
        return self['count']


class collegeWiseStatObj(graphene.ObjectType):
    name = graphene.String()
    count = graphene.Int()
    branchStats = graphene.List(branchWiseStatObj)

    def resolve_name(self, info):
        try:
            return College.objects.get(id=self['college'])
        except College.DoesNotExist:
            return ''

    def resolve_count(self, info):
        return self['count']


class ProshowStatObj(graphene.ObjectType):
    total = graphene.Int()
    collegeWiseStats = graphene.List(collegeWiseStatObj)
    branchWiseStats = graphene.List(branchWiseStatObj)

    def resolve_total(self, info):
        return self.count()

    def resolve_collegeWiseStats(self, info):
        users = self.values_list('user', flat=True)
        profiles = Profile.objects.filter(user__in=users)
        return profiles.values('college').annotate(count=Count('college')).order_by('-count')

    def resolve_branchWiseStats(self, info):
        users = self.values_list('user', flat=True)
        profiles = Profile.objects.filter(user__in=users)
        return profiles.values('branch').annotate(count=Count('branch')).order_by('-count')


class TicketViewObj(graphene.ObjectType):
    ticketName = graphene.String()
    name = graphene.String()
    email = graphene.String()
    rollNo = graphene.String()
    college = graphene.String()
    branch = graphene.String()


class Query(object):
    pass
    #insiderProshowStats = graphene.Field(ProshowStatObj)
    #listTickets = graphene.List(TicketViewObj)
    #generateTicketExport = graphene.Boolean()

    def resolve_generateTicketExport(self, info, **kwargs):
        list = []
        products = Product.objects.filter(name__contains='Amritian Pass').values_list('id', flat=True)
        with open('eng_data.csv', newline='') as csvfile:
            d = csv.reader(csvfile, delimiter=',')
            for user in d:
                name = user[0]
                rollNo = user[1]
                email = user[2]
                branch = user[3]
                division = user[4]
                year = user[5]
                try:
                    profile = Profile.objects.get(user__email=email)
                    order = Order.objects.filter(
                        user=profile.user,
                        transaction__isPaid=True,
                        products__in=products
                    )
                    if order.count() >= 1:
                        status = order.first().products.first().name
                    else:
                        status = 'Not Purchased'
                except Profile.DoesNotExist:
                    status = 'Not Registered'
                obj = [name, status, rollNo, email, branch, division, year]
                print(obj)
                list.append(obj)
        with open('genlist.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(list)
        return True

    @login_required
    def resolve_listTickets(self, info, **kwargs):
        data = []
        if info.context.user.is_superuser():
            products = Product.objects.filter(name__contains='Amritian Pass').values_list('id', flat=True)
            orders = Order.objects.filter(transaction__isPaid=True, products__in=products)
            for o in orders:
                p = Profile.objects.get(user=o.user)
                college = None
                if p.college:
                    college = p.college.name
                obj = {
                    "ticketName": o.products.first().name,
                    "name": o.user.first_name + ' ' + o.user.last_name,
                    "email": o.user.email,
                    "rollNo": p.rollNo,
                    "branch": p.branch,
                    "college": college
                }
                print(obj)
                data.append(obj)
            return data
        return None

    #
    # def resolve_insiderProshowStats(self, info, **kwargs):
    #     products = Product.objects.filter(name__contains='Amritian Pass').values_list('id', flat=True)
    #     return Order.objects.filter(transaction__isPaid=True, products__in=products)
