# Outputs for Bedrock IAM Module

output "bedrock_invoke_policy_arn" {
  description = "ARN of the Bedrock model invocation policy"
  value       = aws_iam_policy.bedrock_invoke.arn
}

output "bedrock_embeddings_policy_arn" {
  description = "ARN of the Bedrock embeddings policy"
  value       = aws_iam_policy.bedrock_embeddings.arn
}

output "bedrock_list_policy_arn" {
  description = "ARN of the Bedrock model listing policy"
  value       = var.enable_model_listing ? aws_iam_policy.bedrock_list[0].arn : null
}

output "bedrock_full_policy_arn" {
  description = "ARN of the combined Bedrock policy"
  value       = var.create_combined_policy ? aws_iam_policy.bedrock_full[0].arn : null
}

output "bedrock_task_role_arn" {
  description = "ARN of the ECS task role with Bedrock access"
  value       = var.create_task_role ? aws_iam_role.bedrock_task_role[0].arn : null
}

output "bedrock_task_role_name" {
  description = "Name of the ECS task role with Bedrock access"
  value       = var.create_task_role ? aws_iam_role.bedrock_task_role[0].name : null
}

output "policy_arns" {
  description = "Map of all policy ARNs created by this module"
  value = {
    invoke     = aws_iam_policy.bedrock_invoke.arn
    embeddings = aws_iam_policy.bedrock_embeddings.arn
    list       = var.enable_model_listing ? aws_iam_policy.bedrock_list[0].arn : null
    full       = var.create_combined_policy ? aws_iam_policy.bedrock_full[0].arn : null
  }
}
