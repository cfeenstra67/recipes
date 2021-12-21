import json

import pulumi
from awacs import s3 as awacs_s3
from awacs.aws import Allow, PolicyDocument, Principal, Statement, Action
from awacs.ecr import (
    BatchGetImage,
    DescribeImages,
    GetDownloadUrlForLayer,
    GetAuthorizationToken,
    BatchCheckLayerAvailability,
)
from awacs.helpers.trust import make_simple_assume_policy, make_service_domain_name
from pulumi_aws import s3, ecr, apprunner, iam


def apprunner_build_assume_role_policy() -> PolicyDocument:
    domain = make_service_domain_name("build.apprunner")
    return make_simple_assume_policy(domain)


def apprunner_tasks_assume_role_policy() -> PolicyDocument:
    domain = make_service_domain_name("tasks.apprunner")
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
                    GetDownloadUrlForLayer,
                    BatchCheckLayerAvailability,
                ],
                Resource=[arn],
            ),
            Statement(
                Sid="2", Effect=Allow, Action=[GetAuthorizationToken], Resource=["*"]
            ),
        ],
    )


def apprunner_instance_policy(bucket: str) -> PolicyDocument:
    return PolicyDocument(
        Version="2012-10-17",
        Id="apprunner-instance-role",
        Statement=[
            Statement(
                Sid="1",
                Effect=Allow,
                Action=[Action("*")],
                Resource=[awacs_s3.ARN(bucket), awacs_s3.ARN(f"{bucket}/*")],
            )
        ],
    )


def main() -> None:
    bucket = s3.Bucket("recipe-scraping", acl="private", force_destroy=True)
    repo = ecr.Repository("recipe-scraping")
    repo_policy = ecr.LifecyclePolicy(
        "recipe-scraping-policy",
        repository=repo.name,
        policy=json.dumps(
            {
                "rules": [
                    {
                        "rulePriority": 1,
                        "description": "Expire images older than 1 day",
                        "selection": {
                            "tagStatus": "untagged",
                            "countType": "sinceImagePushed",
                            "countUnit": "days",
                            "countNumber": 1,
                        },
                        "action": {"type": "expire"},
                    }
                ]
            }
        ),
    )

    apprunner_role = iam.Role(
        "apprunner-recipe-scraping",
        assume_role_policy=apprunner_build_assume_role_policy().to_json(),
        inline_policies=[
            {
                "name": "apprunner-pull-images",
                "policy": repo.arn.apply(
                    lambda x: apprunner_pull_images_policy(x).to_json()
                ),
            }
        ],
    )

    apprunner_instance_role = iam.Role(
        "apprunner-instance-role",
        assume_role_policy=apprunner_tasks_assume_role_policy().to_json(),
        inline_policies=[
            {
                "name": "apprunner-instance-policy",
                "policy": bucket.bucket.apply(
                    lambda x: apprunner_instance_policy(x).to_json()
                ),
            }
        ],
    )

    service_autoscaling_configuration = apprunner.AutoScalingConfigurationVersion(
        "recipe-scraping-autoscaling-config",
        auto_scaling_configuration_name="recipe-scraping",
        max_size=1,
    )

    image_id = repo.repository_url.apply("{}:latest".format)
    output_uri = bucket.bucket.apply("s3://{}/results".format)
    service = apprunner.Service(
        "recipe-scraping",
        service_name="recipe-scraping",
        source_configuration={
            "image_repository": {
                "image_identifier": image_id,
                "image_repository_type": "ECR",
                "image_configuration": {
                    "runtime_environment_variables": {"RECIPES_OUTPUT_URI": output_uri}
                },
            },
            "authentication_configuration": {"access_role_arn": apprunner_role.arn},
        },
        instance_configuration={"instance_role_arn": apprunner_instance_role.arn},
        auto_scaling_configuration_arn=service_autoscaling_configuration.arn,
    )

    pulumi.export("bucket_name", bucket.id)
    pulumi.export("repo_url", repo.repository_url)
    pulumi.export("service_url", service.service_url)


if __name__ == "__main__":
    main()
