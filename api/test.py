"""
Test endpoint to verify Vercel Python runtime is working
"""

def handler(request):
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": '{"ok": true, "message": "Vercel Python runtime is working"}',
    }

# Export for Vercel
app = handler
