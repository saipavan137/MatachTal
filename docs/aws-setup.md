# AWS S3 & GitHub Actions Setup Guide

To deploy your artifacts to AWS S3 using GitHub Actions, you need to configure AWS resources and GitHub Secrets.

## 1. Create an S3 Bucket
1. Log in to the [AWS Management Console](https://console.aws.amazon.com/).
2. Navigate to **S3**.
3. Click **Create bucket**.
4. Enter a globally unique name (e.g., `matchtal-ai-artifacts-YOURNAME`).
5. Choose a region (e.g., `us-east-1`).
6. Uncheck "Block all public access" ONLY if you intend to serve files publicly (for simple artifact storage, keep it blocked).
7. Click **Create bucket**.

## 2. Create an IAM User for GitHub Actions
1. Navigate to **IAM** service in AWS Console.
2. Click **Users** -> **Create user**.
3. Name it `github-actions-deployer`.
4. Select **Attach policies directly**.
5. Search for and select `AmazonS3FullAccess` (Easier) OR create a custom policy with just `s3:PutObject` for your specific bucket (More Secure).
6. Create the user.
7. Click on the newly created user -> **Security credentials** tab.
8. Under **Access keys**, click **Create access key**.
9. Select **Command Line Interface (CLI)**.
10. Copy the **Access Key ID** and **Secret Access Key**. (Save these immediately, you won't see the secret key again).

## 3. Configure GitHub Secrets
1. Go to your GitHub Repository: [https://github.com/saipavan137/MatachTal](https://github.com/saipavan137/MatachTal).
2. Click **Settings** -> **Secrets and variables** -> **Actions**.
3. Click **New repository secret** and add the following:

| Name | Value |
|------|-------|
| `AWS_ACCESS_KEY_ID` | Your Access Key ID from Step 2 |
| `AWS_SECRET_ACCESS_KEY` | Your Secret Access Key from Step 2 |
| `AWS_REGION` | The region of your bucket (e.g., `us-east-1`) |
| `S3_BUCKET_NAME` | The name of the bucket you created in Step 1 |

Once these are set, the GitHub Actions workflow will automatically deploy your code to S3 on every push to the `main` branch.
