# EC2 Deployment Setup Guide (S3 Automated)

This guide helps you set up a single EC2 instance using **AWS CloudFormation** with the template hosted on your S3 bucket.

## 1. Prerequisites
1.  **AWS Account**: You must be logged into the AWS Console.
2.  **Key Pair**: You need an EC2 Key Pair to SSH into your instance.
    *   Go to **EC2 > Key Pairs**.
    *   **Download the file** (e.g., `matchtal-key.pem`).

## 2. Launch Infrastructure via S3
Since we have automatically uploaded your template to S3, you can deploy it directly.

1.  **Get the Template URL**:
    Your template is located at: `https://s3.amazonaws.com/<YOUR-BUCKET-NAME>/infrastructure/ec2.yaml`
    *(Replace `<YOUR-BUCKET-NAME>` with the secret value you set earlier, e.g. `matchtal-ai-artifacts`)*

2.  Go to **CloudFormation** in the AWS Console.
3.  Click **Create stack** > **With new resources (standard)**.
4.  **Prerequisite - Prepare template**: Choose "Template is ready".
5.  **Specify template**: Choose **"Amazon S3 URL"**.
6.  Paste the URL from Step 1.
7.  Click **Next**.
8.  **Stack details**:
    *   **Stack name**: `MatchTal-Stack`
    *   **VpcId**: Select your default VPC (it usually starts with `vpc-`).
    *   **SubnetId**: Select any subnet in that VPC (it usually starts with `subnet-`).
    *   **InstanceType**: `t3.small` (Recommended).
    *   **KeyName**: Select your `matchtal-key`.
    *   **AllowedIP**: `0.0.0.0/0` (or your IP).
9.  Click **Next** -> **Next** -> **Submit**.

## 3. Get Instance IP
1.  Click on the **Outputs** tab of your created CloudFormation stack.
2.  Copy the value of **IPAddress**.

## 4. Configure GitHub Secrets
Go to your repository **Settings > Secrets and variables > Actions** and add:
*   `EC2_HOST`: The IP Address you just copied.
*   `EC2_USER`: `ec2-user`.
*   `EC2_SSH_KEY`: Content of `matchtal-key.pem`.

## 5. Deploy!
Push to `main`. The `Deploy to EC2` workflow will take care of the rest!
