import boto3
import os
import sys

print "----------------------------------"
print "Begin travis doc generation"
print "----------------------------------"

S3_BUCKET = "doctest3"
S3_WEB_URL = "http://doctest3.s3-website.eu-west-2.amazonaws.com"
S3_PATH = "/travis-doc-build/{commit}".format(commit=os.environ["TRAVIS_COMMIT"])

GITHUB_PAGES_URL = "https://manneohrstrom.github.io"
GITHUB_PAGES_PATH = "/jekyll-test"


def upload_folder_to_s3(s3_client, src, dst):
    """
    Upload folder to S3
    """
    names = os.listdir(src)
    for name in names:

        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)

        if os.path.isdir(srcname):
            upload_folder_to_s3(s3_client, srcname, dstname)
        else:
            print "upload '{}' -> '{}'".format(srcname, dstname)
            s3_client.upload_file(srcname, S3_BUCKET, dstname)


root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
doc_script = os.path.join(root_path, "doc_builder", "scripts", "build_docs.sh")
output_path = os.path.join(root_path, "_build")
source_path = os.path.join(root_path, "docs")


if os.environ.get("TRAVIS_BRANCH") != "master" or os.environ.get("TRAVIS_PULL_REQUEST") != "false":

    print "Inside a pull request - will upload preview to S3"

    s3_full_url = "{url}{path}/index.html".format(url=S3_WEB_URL, path=S3_PATH)

    # build the doc
    doc_command = "{script} --url={url} --url-path={path} --source={source} --output={output}".format(
        script=doc_script,
        url=S3_WEB_URL,
        path=S3_PATH,
        source=source_path,
        output=output_path
    )
    print "Building docs: '{}'".format(doc_command)
    if os.system(doc_command) != 0:
        sys.exit(1)

    print 'uploading to s3...'
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.environ["AWS_S3_ACCESS_KEY"],
        aws_secret_access_key=os.environ["AWS_S3_ACCESS_TOKEN"]
    )
    # note: skip the first slash when uploading to S3 in order to generate a correct path.
    upload_folder_to_s3(s3_client, output_path, S3_PATH[1:])

    if os.environ.get("TRAVIS_PULL_REQUEST") != "false":
        print 'generating pull request comment...'
        cmd = "curl -H 'Authorization: token {token}' -X POST ".format(token=os.environ["GITHUB_TOKEN"])
        cmd += "-d '{\"body\": \"[Documentation build](%s)\"}' " % (s3_full_url,)
        cmd += "'https://api.github.com/repos/{repo_slug}/issues/{pull_request}/comments'".format(
            repo_slug=os.environ["TRAVIS_REPO_SLUG"],
            pull_request=os.environ["TRAVIS_PULL_REQUEST"]
        )
        os.system(cmd)

    print "-------------------------------------------------"
    print "Documentation build can be found here:"
    print s3_full_url
    print "-------------------------------------------------"

else:

    print "On master branch - will build for gh-pages branch"

    # build the doc
    doc_command = "{script} --url={url} --url-path={path} --source={source} --output={output}".format(
        script=doc_script,
        url=GITHUB_PAGES_URL,
        path=GITHUB_PAGES_PATH,
        source=source_path,
        output=output_path
    )
    print "Building docs: '{}'".format(doc_command)
    if os.system(doc_command) != 0:
        sys.exit(1)


print "doc generation completed successfully."



