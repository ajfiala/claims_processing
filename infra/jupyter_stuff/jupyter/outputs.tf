output "notebook_url" {
  description = "URL of the SageMaker Jupyter notebook instance"
  value       = aws_sagemaker_notebook_instance.jupyter.url
}

output "role_arn" {
  description = "ARN of the IAM role used by the Jupyter notebook instance"
  value       = aws_iam_role.sagemaker_role.arn
}

output "s3_bucket_name" {
  description = "Name of the S3 bucket used by the Jupyter notebook instance"
  value       = aws_s3_bucket.jupyter_data_bucket.bucket
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket used by the Jupyter notebook instance"
  value       = aws_s3_bucket.jupyter_data_bucket.arn
}