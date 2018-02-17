resource "aws_s3_bucket" "sam" {
  bucket = "shiro-sam"
  acl    = "private"
}

resource "aws_s3_bucket" "dllbot" {
  bucket = "dllbot"
  acl    = "private" 
}

resource "aws_s3_bucket_policy" "dllbot_s3_image" {
  bucket ="${aws_s3_bucket.dllbot.id}"
  policy =<<POLICY
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AddPerm",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::${aws_s3_bucket.dllbot.id}/*"
        }
    ]
}
POLICY
}