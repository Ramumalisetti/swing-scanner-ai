"""Minimal test handler"""

def handler(request):
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/plain"},
        "body": "OK",
    }

# Export for Vercel
app = handler




