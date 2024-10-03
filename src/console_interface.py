import os
import grpc
import object_storage_pb2
import object_storage_pb2_grpc

class ObjectStorageClient:
    def __init__(self, address='localhost:23009'):
        self.channel = grpc.insecure_channel(
            address,
            options=[
                ('grpc.max_send_message_length', 50 * 1024 * 1024),  # 50 MB
                ('grpc.max_receive_message_length', 50 * 1024 * 1024)  # 50 MB
            ]
        )
        self.stub = object_storage_pb2_grpc.ObjectStorageServiceStub(self.channel)
        self.token = None

    def authenticate(self, username, password):
        request = object_storage_pb2.AuthenticationRequest(username=username, password=password)
        response = self.stub.Authenticate(request)
        self.token = response.token

    def upload_file(self, bucket_name, object_key, data, compress):
        request = object_storage_pb2.UploadObjectRequest(
            token=self.token,
            bucket_name=bucket_name,
            object_key=object_key,
            data=data,
            compress=compress
        )
        return self.stub.UploadObject(request)

    def get_object(self, bucket_name, object_key):
        request = object_storage_pb2.GetObjectRequest(
            token=self.token,
            bucket_name=bucket_name,
            object_key=object_key
        )
        return self.stub.GetObject(request)

    def list_objects(self, bucket_name):
        request = object_storage_pb2.ListObjectsRequest(
            token=self.token,
            bucket_name=bucket_name
        )
        return self.stub.ListObjects(request)

    def delete_object(self, bucket_name, object_key):
        request = object_storage_pb2.DeleteObjectRequest(
            token=self.token,
            bucket_name=bucket_name,
            object_key=object_key
        )
        return self.stub.DeleteObject(request)

def print_menu():
    print("\n=== Object Storage Console ===")
    print("1. Authenticate")
    print("2. Upload file")
    print("3. Download file")
    print("4. List files")
    print("5. Delete file")
    print("6. Exit")
    print("============================")

def authenticate(client):
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    try:
        client.authenticate(username, password)
        print("Authentication successful")
    except grpc.RpcError as e:
        print(f"Authentication failed: {e.details()}")

def upload_file(client):
    bucket_name = input("Enter bucket name: ")
    file_path = input("Enter file path: ")
    object_key = input("Enter object key: ")
    compress = input("Compress file? (y/n): ").lower() == 'y'

    if not os.path.exists(file_path):
        print("File not found.")
        return

    try:
        with open(file_path, "rb") as file:
            data = file.read()
        
        response = client.upload_file(bucket_name, object_key, data, compress)
        print(f"File uploaded successfully. Message: {response.message}")
    except grpc.RpcError as e:
        print(f"Error uploading file: {e.details()}")

def download_file(client):
    bucket_name = input("Enter bucket name: ")
    object_key = input("Enter object key: ")
    save_path = input("Enter save path: ")

    try:
        response = client.get_object(bucket_name, object_key)
        with open(save_path, "wb") as file:
            file.write(response.data)
        print(f"File downloaded successfully to {save_path}")
    except grpc.RpcError as e:
        print(f"Error downloading file: {e.details()}")

def list_files(client):
    bucket_name = input("Enter bucket name: ")
    
    try:
        response = client.list_objects(bucket_name)
        if not response.objects:
            print(f"No objects found in bucket '{bucket_name}'")
        else:
            print(f"\nObjects in bucket '{bucket_name}':")
            for obj in response.objects:
                print(f"- {obj.object_key} (Size: {obj.size} bytes, Created: {obj.created_at})")
    except grpc.RpcError as e:
        print(f"Error listing files: {e.details()}")

def delete_file(client):
    bucket_name = input("Enter bucket name: ")
    object_key = input("Enter object key: ")

    try:
        response = client.delete_object(bucket_name, object_key)
        print(f"File deleted successfully. Message: {response.message}")
    except grpc.RpcError as e:
        print(f"Error deleting file: {e.details()}")

def main():
    client = ObjectStorageClient()

    while True:
        print_menu()
        choice = input("Enter your choice: ")

        if choice == '1':
            authenticate(client)
        elif choice == '2':
            if not client.token:
                print("Please authenticate first")
            else:
                upload_file(client)
        elif choice == '3':
            if not client.token:
                print("Please authenticate first")
            else:
                download_file(client)
        elif choice == '4':
            if not client.token:
                print("Please authenticate first")
            else:
                list_files(client)
        elif choice == '5':
            if not client.token:
                print("Please authenticate first")
            else:
                delete_file(client)
        elif choice == '6':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()