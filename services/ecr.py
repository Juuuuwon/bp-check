from models import RuleCheckResult, RuleChecker
from functools import cached_property
import boto3


class ECRRuleChecker(RuleChecker):
    def __init__(self):
        self.client = boto3.client("ecr")

    @cached_property
    def repositories(self):
        return self.client.describe_repositories()["repositories"]

    def ecr_private_image_scanning_enabled(self):
        compliant_resource = []
        non_compliant_resources = []

        for repository in self.repositories:
            if repository["imageScanningConfiguration"]["scanOnPush"] == True:
                compliant_resource.append(repository["repositoryArn"])
            else:
                non_compliant_resources.append(repository["repositoryArn"])

        return RuleCheckResult(
            passed=not non_compliant_resources,
            compliant_resources=compliant_resource,
            non_compliant_resources=non_compliant_resources,
        )

    def ecr_private_lifecycle_policy_configured(self):
        compliant_resource = []
        non_compliant_resources = []

        for repository in self.repositories:
            try:
                response = self.client.get_lifecycle_policy(
                    registryId=repository["registryId"],
                    repositoryName=repository["repositoryName"],
                )
                compliant_resource.append(repository["repositoryArn"])
            except Exception as e:
                if e.__class__.__name__ == "LifecyclePolicyNotFoundException":
                    non_compliant_resources.append(repository["repositoryArn"])
                else:
                    raise e

        return RuleCheckResult(
            passed=not non_compliant_resources,
            compliant_resources=compliant_resource,
            non_compliant_resources=non_compliant_resources,
        )

    def ecr_private_tag_immutability_enabled(self):
        compliant_resource = []
        non_compliant_resources = []

        for repository in self.repositories:
            if repository["imageTagMutability"] == "IMMUTABLE":
                compliant_resource.append(repository["repositoryArn"])
            else:
                non_compliant_resources.append(repository["repositoryArn"])

        return RuleCheckResult(
            passed=not non_compliant_resources,
            compliant_resources=compliant_resource,
            non_compliant_resources=non_compliant_resources,
        )

    def ecr_kms_encryption_1(self):
        compliant_resource = []
        non_compliant_resources = []

        for repository in self.repositories:
            if repository["encryptionConfiguration"]["encryptionType"] == "KMS":
                compliant_resource.append(repository["repositoryArn"])
            else:
                non_compliant_resources.append(repository["repositoryArn"])

        return RuleCheckResult(
            passed=not non_compliant_resources,
            compliant_resources=compliant_resource,
            non_compliant_resources=non_compliant_resources,
        )


rule_checker = ECRRuleChecker
