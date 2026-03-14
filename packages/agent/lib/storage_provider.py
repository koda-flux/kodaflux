import os
from pathlib import PurePosixPath

import boto3
from botocore.exceptions import ClientError


class StorageProvider:
    """
    Wraps a DigitalOcean Spaces bucket and exposes all file operations
    the storer agent needs to build and publish a Docsify site.
    """

    def __init__(self):
        self.__endpoint = os.getenv("DIGITALOCEAN_SPACES_ENDPOINT")
        self.__bucket = os.getenv("DIGITALOCEAN_SPACES_BUCKET_NAME", "kodaflux-assets")
        self.__client = boto3.client(
            "s3",
            region_name=os.getenv("DIGITALOCEAN_SPACES_REGION", "fra1"),
            endpoint_url=self.__endpoint,
            aws_access_key_id=os.getenv("DIGITALOCEAN_SPACES_KEY_ID"),
            aws_secret_access_key=os.getenv("DIGITALOCEAN_SPACES_SECRET_KEY"),
        )

    def write_file(
        self,
        key: str,
        content: str,
        content_type: str = "text/markdown",
        public: bool = True,
    ) -> str:
        """
        Write a single text file to the bucket.

        Args:
            key:          Full path inside the bucket, e.g. "my-project/docs/react.md"
            content:      File content as a string.
            content_type: MIME type. Defaults to "text/markdown".
            public:       If True, the file is publicly readable. Defaults to True.

        Returns:
            The public URL of the written file.
        """
        extra_args = {"ContentType": content_type}
        if public:
            extra_args["ACL"] = "public-read"

        self.__client.put_object(
            Bucket=self.__bucket,
            Key=key,
            Body=content.encode("utf-8"),
            **extra_args,
        )
        return self._public_url(key)

    def read_file(self, key: str) -> str:
        """
        Read a file from the bucket and return its content as a string.

        Args:
            key: Full path inside the bucket.

        Returns:
            File content as a string.

        Raises:
            FileNotFoundError: If the key does not exist in the bucket.
        """
        try:
            response = self.__client.get_object(Bucket=self.__bucket, Key=key)
            return response["Body"].read().decode("utf-8")
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "NoSuchKey":
                raise FileNotFoundError(f"Key not found in bucket: {key}") from exc
            raise

    def delete_file(self, key: str) -> None:
        """
        Delete a single file from the bucket.

        Args:
            key: Full path inside the bucket.
        """
        self.__client.delete_object(Bucket=self.__bucket, Key=key)

    def file_exists(self, key: str) -> bool:
        """
        Check whether a key exists in the bucket without downloading it.

        Args:
            key: Full path inside the bucket.

        Returns:
            True if the key exists, False otherwise.
        """
        try:
            self.__client.head_object(Bucket=self.__bucket, Key=key)
            return True
        except ClientError:
            return False

    def write_many(
        self,
        files: dict[str, str],
        content_type: str = "text/markdown",
        public: bool = True,
    ) -> dict[str, str]:
        """
        Write multiple files to the bucket in one call.

        Args:
            files:        Dict of { key: content } pairs.
            content_type: MIME type applied to all files. Defaults to "text/markdown".
            public:       If True, all files are publicly readable.

        Returns:
            Dict of { key: public_url } for every file written.
        """
        urls: dict[str, str] = {}
        for key, content in files.items():
            # html files need the correct content type so browsers render them
            resolved_type = "text/html" if key.endswith(".html") else content_type
            urls[key] = self.write_file(key, content, resolved_type, public)
        return urls

    def list_files(self, prefix: str = "") -> list[str]:
        """
        List all keys in the bucket that start with the given prefix.

        Args:
            prefix: Optional key prefix to filter by, e.g. "my-project/".

        Returns:
            List of matching keys.
        """
        keys: list[str] = []
        paginator = self.__client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self.__bucket, Prefix=prefix):
            for obj in page.get("Contents", []):
                keys.append(obj["Key"])
        return keys

    def delete_folder(self, prefix: str) -> int:
        """
        Delete all files whose key starts with the given prefix.
        Useful for clearing a project folder before re-publishing.

        Args:
            prefix: Key prefix to delete, e.g. "my-project/".

        Returns:
            Number of files deleted.
        """
        keys = self.list_files(prefix)
        if not keys:
            return 0

        # Spaces supports batch delete of up to 1000 objects per request
        objects = [{"Key": k} for k in keys]
        for i in range(0, len(objects), 1000):
            self.__client.delete_objects(
                Bucket=self.__bucket,
                Delete={"Objects": objects[i : i + 1000]},
            )
        return len(keys)

    def get_project_url(self, project_name: str) -> str:
        """
        Returns the public URL of a project's index.html — the entry
        point for the generated Docsify site.

        Args:
            project_name: The project folder name inside the bucket.

        Returns:
            Full public URL to the project's index.html.
        """
        key = str(PurePosixPath(project_name) / "index.html")
        return self._public_url(key)

    def _public_url(self, key: str) -> str:
        endpoint = self.__endpoint.rstrip("/")
        return f"{endpoint}/{self.__bucket}/{key}"
