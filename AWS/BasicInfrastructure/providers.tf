

# aut@r: Susana Edith Barrientos Galicia
# 14 Febrary 2025
# PoC Unos

terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      #version = "~> 5.0"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region = "us-east-1"
  #shared_config_files      = ["~/.aws/confing"]
  #shared_credentials_files = ["/.aws/credentials"]
  #profile = "default"
  access_key = ""
  secret_key = ""
}
