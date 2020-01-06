import graphene
from .models import Question, Answer


class AnswerObj(graphene.ObjectType):
    answer = graphene.String()
    created = graphene.String()


class QuestionObj(graphene.ObjectType):
    created = graphene.String()
    question = graphene.String()
    id = graphene.Int()
    answers = graphene.List(AnswerObj)

    def resolve_answers(self, info):
        return Answer.objects.filter(question=self.id).order_by('-created')


class Query(object):
    viewQuestions = graphene.List(QuestionObj)

    @staticmethod
    def resolve_viewQuestions(self, info):
        return Question.objects.all()
