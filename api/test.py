"""Test endpoint"""
import json

def handler(request):
    try:
        # Debug - see what we're actually receiving
        request_type = type(request).__name__
        
        # Try to extract query string
        query_string = ""
        if isinstance(request, dict):
            # WSGI environ dict
            query_string = request.get('QUERY_STRING', '')
        elif hasattr(request, 'query_string'):
            query_string = request.query_string
        elif hasattr(request, 'url'):
            if '?' in request.url:
                query_string = request.url.split('?', 1)[1]
        
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "ok": True, 
                "message": "test works",
                "request_type": request_type,
                "query_string": query_string,
            }),
        }
    except Exception as e:
        import traceback
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "ok": False, 
                "error": str(e),
                "traceback": traceback.format_exc(),
            }),
        }


