import grpc
from concurrent import futures
import object_storage_pb2
import object_storage_pb2_grpc
from storage.object_storage import ObjectStorage
from datetime import datetime
import logging
from auth.jwt_manager import generate_token, verify_token
from auth.user_manager import authenticate_user
from functools import wraps

logging.basicConfig(filename='server.log', level=logging.ERROR)
grpc_logger = logging.getLogger('grpc')
grpc_logger.setLevel(logging.ERROR)

def auth_middleware(func):
    @wraps(func)
    def wrapper(self, request, context):
        if hasattr(request, 'token'):
            try:
                payload = verify_token(request.token)
                context.user_id = payload['user_id']
                context.role = payload['role']
            except ValueError as e:
                context.abort(grpc.StatusCode.UNAUTHENTICATED, str(e))
        else:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Token is required")
        return func(self, request, context)
    return wrapper

def admin_required(func):
    @wraps(func)
    def wrapper(self, request, context):
        if not hasattr(context, 'role') or context.role != 'admin':
            context.abort(grpc.StatusCode.PERMISSION_DENIED, "Admin access required")
        return func(self, request, context)
    return wrapper

class ObjectStorageServicer(object_storage_pb2_grpc.ObjectStorageServiceServicer):
    def __init__(self, storage):
        self.storage = storage

    def Authenticate(self, request, context):
        user = authenticate_user(request.username, request.password)
        if user:
            token = generate_token(user['user_id'], user['role'])
            return object_storage_pb2.AuthenticationResponse(token=token)
        else:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid credentials")

    @auth_middleware
    def UploadObject(self, request, context):
        try:
            storage_object = self.storage.upload_file(
                request.bucket_name,
                request.object_key,
                request.data,
                context.user_id,
                request.compress
            )
            return object_storage_pb2.UploadObjectResponse(
                message="Object uploaded successfully",
                metadata=self._metadata_to_proto(storage_object.metadata)
            )
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, str(e))

    @auth_middleware
    def GetObject(self, request, context):
        try:
            storage_object = self.storage.get_object(request.bucket_name, request.object_key)
            if storage_object.metadata.owner_id != context.user_id and context.role != 'admin':
                context.abort(grpc.StatusCode.PERMISSION_DENIED, "Access denied")
            return object_storage_pb2.GetObjectResponse(
                metadata=self._metadata_to_proto(storage_object.metadata),
                data=storage_object.data
            )
        except FileNotFoundError:
            context.abort(grpc.StatusCode.NOT_FOUND, "Object not found")
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, str(e))

    @auth_middleware
    def ListObjects(self, request, context):
        try:
            objects = self.storage.list_objects(request.bucket_name)
            if context.role != 'admin':
                objects = [obj for obj in objects if obj.owner_id == context.user_id]
            return object_storage_pb2.ListObjectsResponse(
                objects=[self._metadata_to_proto(obj) for obj in objects]
            )
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, str(e))

    @auth_middleware
    @admin_required
    def DeleteObject(self, request, context):
        try:
            self.storage.delete_object(request.bucket_name, request.object_key)
            return object_storage_pb2.DeleteObjectResponse(message="Object deleted successfully")
        except FileNotFoundError:
            context.abort(grpc.StatusCode.NOT_FOUND, "Object not found")
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, str(e))

    def _metadata_to_proto(self, metadata):
        return object_storage_pb2.ObjectMetadata(
            object_key=metadata.object_key,
            bucket_name=metadata.bucket_name,
            size=metadata.size,
            md5_hash=metadata.md5_hash,
            mime_type=metadata.mime_type,
            created_at=metadata.created_at.isoformat(),
            modified_at=metadata.modified_at.isoformat(),
            owner_id=metadata.owner_id,
            is_compressed=metadata.is_compressed
        )

    
def serve():
    storage = ObjectStorage("/tmp/object_storage")
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ('grpc.max_send_message_length', 50 * 1024 * 1024),  # 50 MB
            ('grpc.max_receive_message_length', 50 * 1024 * 1024)  # 50 MB
        ]
    )
    object_storage_pb2_grpc.add_ObjectStorageServiceServicer_to_server(
        ObjectStorageServicer(storage), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC server started on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()