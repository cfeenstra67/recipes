import dataclasses as dc

import pulumi
from awacs.aws import (
    Allow,
    PolicyDocument,
    Principal,
    Statement
)
from awacs.ecr import (
    BatchGetImage,
    DescribeImages,
    GetDownloadUrlForLayer
)
from awacs.helpers.trust import (
    make_simple_assume_policy,
    make_service_domain_name
)
from pulumi_aws import s3, ecr, apprunner, iam


@dc.dataclass(frozen=True)
class AWSLiteral:
    """
    Literal for use w/ awacs
    """
    value: str

    def JSONrepr(self) -> str:
        return self.value


def apprunner_assume_role_policy() -> PolicyDocument:
    domain = make_service_domain_name("build.apprunner")
    return make_simple_assume_policy(domain)


def apprunner_pull_images_policy(arn: str) -> PolicyDocument:
    return PolicyDocument(
        Version="2012-10-17",
        Id="apprunner-pull-images",
        Statement=[
            Statement(
                Sid="1",
                Effect=Allow,
                Action=[
                    BatchGetImage,
                    DescribeImages,
                    GetDownloadUrlForLayer
                ],
                Resource=[AWSLiteral(arn)]
            )
        ]
    )


def main() -> None:
    bucket = s3.Bucket(
        "recipe-scraping",
        acl="private",
        force_destroy=True
    )
    repo = ecr.Repository(
        "recipe-scraping"
    )

    image_id = repo.repository_url.apply("{}:latest".format)
    output_uri = bucket.bucket.apply("s3://{}/results".format)

    apprunner_role = iam.Role(
        "apprunner-recipe-scraping",
        assume_role_policy=apprunner_assume_role_policy().to_json(),
        inline_policies=[
            {
                "name": "apprunner-pull-images",
                "policy": repo.arn.apply(lambda x: apprunner_pull_images_policy(x).to_json())
            }
        ]
    )

    service = apprunner.Service(
        "recipe-scraping",
        service_name="recipe-scraping",
        source_configuration={
            "image_repository": {
                "image_identifier": image_id,
                "image_repository_type": "ECR",
                "image_configuration": {
                    "runtime_environment_variables": {
                        "RECIPES_OUTPUT_URI": output_uri
                    }
                }
            },
            "authentication_configuration": {
                "access_role_arn": apprunner_role.arn
            }
        }
    )

    pulumi.export("bucket_name", bucket.id)
    pulumi.export("repo_url", repo.repository_url)


if __name__ == '__main__':
    main()
