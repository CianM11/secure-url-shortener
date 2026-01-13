import json
import os
import time
import base64
import hashlib
import boto3
from botocore.exceptions import ClientError

TABLE_NAME = os.environ["TABLE_NAME"]
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)

def _resp(status, body, headers=None):
    h = {"Content-Type": "application/json"}
    if headers:
        h.update(headers)
    return {"statusCode": status, "headers": h, "body": json.dumps(body)}

def _short_code(url: str) -> str:
    # deterministic short code (simple + fine for demo)
    digest = hashlib.sha256(url.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest[:6]).decode("utf-8").rstrip("=")

def handler(event, context):
    # Works with API Gateway HTTP API (v2)
    method = event.get("requestContext", {}).get("http", {}).get("method", "")
    path_params = event.get("pathParameters") or {}

    if method == "POST":
        try:
            body = json.loads(event.get("body") or "{}")
            target_url = body.get("url")
            if not target_url or not isinstance(target_url, str):
                return _resp(400, {"error": "Missing or invalid 'url'."})

            code = _short_code(target_url)
            now = int(time.time())

            table.put_item(
                Item={
                    "short_code": code,
                    "target_url": target_url,
                    "created_at": now,
                    "clicks": 0,
                },
                ConditionExpression="attribute_not_exists(short_code)"
            )

            return _resp(200, {"short_code": code, "target_url": target_url})
        except ClientError as e:
            # If already exists, just return it (idempotent)
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return _resp(200, {"short_code": _short_code(body.get("url", "")), "target_url": body.get("url")})
            return _resp(500, {"error": "DynamoDB error", "detail": str(e)})
        except Exception as e:
            return _resp(500, {"error": "Server error", "detail": str(e)})

    if method == "GET":
        code = path_params.get("code")
        if not code:
            return _resp(400, {"error": "Missing short code."})

        try:
            res = table.get_item(Key={"short_code": code})
            item = res.get("Item")
            if not item:
                return _resp(404, {"error": "Not found"})

            # increment clicks (best-effort)
            table.update_item(
                Key={"short_code": code},
                UpdateExpression="SET clicks = if_not_exists(clicks, :z) + :one",
                ExpressionAttributeValues={":one": 1, ":z": 0},
            )

            # For redirects: API Gateway can return 302 with Location header.
            return {
                "statusCode": 302,
                "headers": {"Location": item["target_url"]},
                "body": ""
            }
        except Exception as e:
            return _resp(500, {"error": "Server error", "detail": str(e)})

    return _resp(405, {"error": "Method not allowed"})
