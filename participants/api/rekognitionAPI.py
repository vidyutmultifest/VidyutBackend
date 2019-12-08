import graphene
import boto3
from graphql_jwt.decorators import login_required

from framework.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY


class RekognitionObj(graphene.ObjectType):
    jsonData = graphene.String()


class Query(object):
    detectFace = graphene.Field(RekognitionObj)
    detectText = graphene.Field(RekognitionObj)

    @login_required
    def resolve_detectFace(self, info, **kwargs):
        rekognition = boto3.client(
            "rekognition",
            'ap-south-1',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        photo = info.context.FILES['photo']
        return RekognitionObj(jsonData=str(rekognition.detect_faces(
            Image={
                "Bytes": photo.read()
            },
            Attributes=["DEFAULT"],
        )))

    @login_required
    def resolve_detectText(self, info, **kwargs):
        rekognition = boto3.client(
            "rekognition",
            'ap-south-1',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        photo = info.context.FILES['photo']
        return RekognitionObj(jsonData=str(rekognition.detect_text(
            Image={
                "Bytes": photo.read()
            }
        )))