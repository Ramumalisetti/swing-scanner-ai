"""Minimal test handler"""

def handler(request=None, *args, **kwargs):
    """Handle both serverless and WSGI invocations"""
    try:
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "text/plain"},
            "body": "OK",
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "text/plain"},
            "body": f"Error: {str(e)}",
        }

# Export for Vercel - create a callable wrapper
class AppWrapper:
    def __call__(self, request=None, start_response=None, *args, **kwargs):
        """Support both WSGI and direct invocation"""
        result = handler(request, *args, **kwargs)
        
        # If start_response is provided (WSGI), use that
        if start_response:
            status = f"{result['statusCode']} OK"
            response_headers = [(k, v) for k, v in result['headers'].items()]
            start_response(status, response_headers)
            return [result['body'].encode() if isinstance(result['body'], str) else result['body']]
        
        # Otherwise return the dict (serverless)
        return result

app = AppWrapper()





