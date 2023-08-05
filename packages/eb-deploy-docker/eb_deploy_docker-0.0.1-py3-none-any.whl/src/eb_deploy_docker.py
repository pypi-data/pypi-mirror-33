#!/usr/bin/python

import os
import json
import yaml
import argparse
from datetime import datetime
from subprocess import check_output, CalledProcessError

import boto3
from botocore.exceptions import ProfileNotFound, NoCredentialsError, ClientError

REGION_KEY = "Region"
APPLICATION_KEY = "Application name"
ENVIRONMENT_NAME_KEY = "Environment details for"
ENVIRONMENT_ID_KEY = "Environment ID"

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="JSON file to deploy. Defaults to Dockerrun.aws.json", default="Dockerrun.aws.json", nargs='?')
    parser.add_argument("--version-label", help="A label identifying this version.")
    parser.add_argument("--profile", help="Use a specific profile from your credential file.")

    parser.add_argument("--application-name", help="The name of the application with which the environment is associated.")
    parser.add_argument("--environment-name", help="The name of the environment to update")
    parser.add_argument("--environment-id", help="The ID of the environment to update.")
    parser.add_argument("--region", help="The region to use.")

    return parser

def get_account_id():
    client = boto3.client("sts")
    return client.get_caller_identity()["Account"]

def get_environment_info(profile):
    cmd = ["eb", "status"] + (["--profile", profile] if profile else [])

    try:
        eb_status = check_output(cmd, encoding="utf-8")
    except CalledProcessError as e:
        print(e.output)
        exit(1)

    if eb_status.startswith("ERROR:"):
        print(eb_status)
        exit(1)

    environment = {}
    for line in eb_status.splitlines():
        items = line.split(":")
        environment[items[0].strip()] = "".join(items[1:]).strip()

    return environment

def get_git_commit():
    return check_output("git log -1 --pretty=%B".split(), encoding="utf-8").strip()

def create_version_label():
    return get_git_commit() + datetime.now().strftime(" %y%m%d_%H%M%S")

def upload_dockerrun(filename, bucket):
    client = boto3.client("s3")
    try:
        upload_key = datetime.now().strftime("%Y%m%d%H%M%S-Dockerrun.aws.json")
        client.upload_file(filename, bucket, upload_key)
        return upload_key
    except ClientError as e:
        print(e)
        exit(1)

def create_application_version(dockerrun, bucket, version, application):
    client = boto3.client("elasticbeanstalk")
    try:
        res = client.create_application_version(
            ApplicationName = application,
            VersionLabel = version,
            SourceBundle = {
                'S3Bucket': bucket,
                'S3Key': dockerrun
            },
            AutoCreateApplication = False
        )

        return res["ApplicationVersion"]["Status"]
    except ClientError as e:
        print(e)
        exit(1)

def update_environment(application, environment_name, environment_id, version):
    client = boto3.client("elasticbeanstalk")
    try:
        res = client.update_environment(
            ApplicationName = application,
            EnvironmentName = environment_name,
            EnvironmentId = environment_id,
            VersionLabel = version
        )
    except ClientError as e:
        print(e)
        exit(1)

def validate_json(filename):
    with open(filename) as f:
        try:
            json.load(f)
        except ValueError as e:
            print("Invalid JSON:", e)
            exit(1)

def get_config_profile():
    EB_CONFIG = ".elasticbeanstalk/config.yml"

    if os.path.exists(EB_CONFIG):
        fp = open(EB_CONFIG)
        data = yaml.load(fp)

        return data["global"].get("profile", None)

    return None

def main():
    parser = get_parser()
    args = parser.parse_args()

    # Verify the json
    filename = args.file

    if not os.path.exists(filename):
        parser.error("%s does not exists" % filename)

    validate_json(filename)

    # verify the profile
    profile = args.profile or get_config_profile()

    if profile:
        try:
            boto3.setup_default_session(profile_name=profile)
        except ProfileNotFound as e:
            print("Could not find profile", profile)
            exit(1)

    # get the account id
    try:
        account_id = get_account_id()
    except NoCredentialsError as e:
        print(e)
        exit(1)

    # get the environment using 'eb status' if no parameters given
    application_name = args.application_name
    environment_name = args.environment_name
    environment_id = args.environment_id
    region = args.region

    if not application_name and not environment_name and not environment_id and not region:
        env = get_environment_info(profile)
        application_name = env[APPLICATION_KEY]
        environment_name = env[ENVIRONMENT_NAME_KEY]
        environment_id = env[ENVIRONMENT_ID_KEY]
        region = env[REGION_KEY]
    elif application_name and (environment_name or environment_id) and region:
        # we have all the required arguments
        pass
    else:
        parser.error("Missing arguments. Application name, region and environment (name or id) required")

    # get the version from git if no parameters given
    version_label = args.version_label or create_version_label()

    print("Deploying version \"%s\" of %s on application %s, environment %s, region %s" % (
        version_label, filename, application_name, (environment_name or environment_id), region
    ))

    # Upload Dockerrun.aws.json to S3
    bucket = "elasticbeanstalk-%s-%s" % (region, account_id)

    uploaded = upload_dockerrun(filename, bucket)
    print("Uploaded Dockerrun to ", bucket)

    # Create application version
    status = create_application_version(uploaded, bucket, version_label, application_name)

    if status != "Failed":
        print("Created application version")

    # Deploy
    update_environment(application_name, environment_name, environment_id, version_label)

    print("Deploy started, you can check the progress with 'eb events -f'")

if __name__ == "__main__":
    main()