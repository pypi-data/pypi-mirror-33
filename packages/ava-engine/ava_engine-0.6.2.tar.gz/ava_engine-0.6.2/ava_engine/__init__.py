#!/usr/bin/env python
# -*- coding: utf-8 -*-
import grpc

from ava_engine.ava.engine_api_pb2 import Features, StatusRequest, InitializeRequest
from ava_engine.ava.engine_core_pb2 import BoundingBox

from ava_engine.ava.feeds_api_pb2 import \
    CreateFeedRequest, \
    DeleteFeedRequest, \
    GetFeedRequest, \
    ListFeedsRequest, \
    ConfigureFeedRequest
from ava_engine.ava.images_api_pb2 import GetImageRequest, SearchImagesRequest, SummaryImagesRequest
from ava_engine.ava.feature_classification_pb2 import ClassifyRequest
from ava_engine.ava.feature_detection_pb2 import DetectRequest
from ava_engine.ava.feature_face_recognition_pb2 import \
    AddFaceItem, \
    AddFaceRequest, \
    ListFacesRequest, \
    AddIdentityRequest, \
    UpdateIdentityRequest, \
    RemoveIdentityRequest, \
    ListIdentitiesRequest, \
    RecognizeFaceRequest

from ava_engine.ava.engine_core_pb2 import ImageItem
from ava_engine.ava.service_api_pb2_grpc import EngineApiDefStub, FeedsApiDefStub, \
    ClassificationApiDefStub, DetectionApiDefStub, FaceRecognitionApiDefStub, ImagesApiDefStub


class _ClassificationFeature:
    def __init__(self, channel):
        self._channel = channel
        self._stub = ClassificationApiDefStub(self._channel)

    def detect(self, images, classes):
        return self._stub.Detect(ClassifyRequest(images=images, classes=classes))

class _DetectionFeature:
    def __init__(self, channel):
        self._channel = channel
        self._stub = DetectionApiDefStub(self._channel)

    def detect(self, images):
        return self._stub.Detect(DetectRequest(images=images))


class _FaceRecognitionFeature:
    def __init__(self, channel):
        self._channel = channel
        self._stub = FaceRecognitionApiDefStub(self._channel)

    # Faces
    def add_face(self, face_thumbnails):
        faces = [AddFaceItem(data=data) for data in face_thumbnails]
        raise self._stub.AddFace(AddFaceRequest(faces=faces))

    def list_faces(self):
        return self._stub.ListFaces(ListFacesRequest())

    # def remove_face(self, face_id):
    #     raise NotImplementedError

    # Identities
    def add_identity(self, identity):
        return self._stub.AddIdentity(AddIdentityRequest(
            id=identity.get('id'),
            name=identity.get('name'),
            face_ids=identity.get('face_ids'),
        ))

    def update_identity(self, update):
        return self._stub.UpdateIdentity(UpdateIdentityRequest(
            id=update.get('id'),
            name=update.get('name'),
            add_face_ids=update.get('add_face_ids'),
            remove_face_ids=update.get('remove_face_ids'),
        ))

    def remove_identity(self, identity_id):
        return self._stub.RemoveIdentity(RemoveIdentityRequest(
            id=identity_id
        ))

    def list_identities(self):
        return self._stub.ListIdentities(ListIdentitiesRequest())

    # Recognition and detection
    def recognize(self, images):
        return self._stub.Recognize(RecognizeFaceRequest(images=images))

    # def detect(self, images):
    #     raise NotImplementedError


class _Feeds:
    def __init__(self, channel):
        self._channel = channel
        self._stub = FeedsApiDefStub(self._channel)

    def create(self, feed_id):
        return self._stub.CreateFeed(CreateFeedRequest(id=feed_id))

    def delete(self, feed_id):
        return self._stub.DeleteFeed(DeleteFeedRequest(id=feed_id))

    def get(self, feed_id):
        return self._stub.GetFeed(GetFeedRequest(id=feed_id))

    def list(self):
        return self._stub.ListFeeds(ListFeedsRequest())

    def configure(self, feed_id, features):
        return self._stub.ConfigureFeed(ConfigureFeedRequest(
            id=feed_id,
            features=features,
        ))


class _Images:
    def __init__(self, channel):
        self._channel = channel
        self._stub = ImagesApiDefStub(self._channel)

    def get(self, image_id):
        return self._stub.GetImage(GetImageRequest(id=image_id))

    def search(self, options):
        req = SearchImagesRequest(
            before=options.get('before'),
            after=options.get('after'),
            feed_ids=options.get('feed_ids'),
            limit=options.get('limit'),
            offset=options.get('offset'),
            classification=options.get('classification'),
            detection=options.get('detection'),
            face_recognition=options.get('face_recognition'),
        )
        return self._stub.SearchImages(req)

    def summary(self, options):
        req = SummaryImagesRequest(
            before=options.get('before'),
            after=options.get('after'),
            feed_ids=options.get('feed_ids'),
            classification=options.get('classification'),
            detection=options.get('detection'),
            face_recognition=options.get('face_recognition'),
        )
        return self._stub.SummaryImages(req)


class AvaEngineClient:
    def __init__(self, host='localhost', port=50051):
        self._host = host
        self._port = port

        self._channel = grpc.insecure_channel('{host}:{port}'.format(host=host, port=port))
        self._stub = EngineApiDefStub(self._channel)

        self.classification = _ClassificationFeature(self._channel)
        self.detection = _DetectionFeature(self._channel)
        self.face_recognition = _FaceRecognitionFeature(self._channel)
        self.feeds = _Feeds(self._channel)
        self._images = _Images(self._channel)

    @property
    def images(self):
        return self._images

    def status(self):
        return self._stub.Status(StatusRequest())

    def initialize(self, configuration):
        return self._stub.Initialize(InitializeRequest(
            features=Features(
                classification=configuration.get('classification'),
                detection=configuration.get('detection'),
                face_recognition=configuration.get('face_recognition'),
            )
        ))
