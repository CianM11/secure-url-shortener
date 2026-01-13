terraform {
  backend "s3" {
    bucket         = "secure-url-shortener-tfstate-69df0e"
    key            = "dev/terraform.tfstate"
    region         = "eu-west-1"
    dynamodb_table = "secure-url-shortener-tflock"
    encrypt        = true
  }
}
