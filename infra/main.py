import pulumi
from pulumi_aws import s3, ecr


def main():
    bucket = s3.Bucket(
        "recipe-scraping",
        acl="private",
        force_destroy=True
    )

    repo = ecr.Repository("recipe-scraping")

    # Export the name of the bucket
    pulumi.export('bucket_name', bucket.id)
