from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.request
import os

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            event = json.loads(post_data.decode('utf-8'))
            
            # Extract fields
            kind = event.get("involvedObject", {}).get("kind", "Unknown")
            name = event.get("involvedObject", {}).get("name", "unknown")
            namespace = event.get("involvedObject", {}).get("namespace", "unknown")
            message = event.get("message", "")
            severity = event.get("severity", "info")
            revision = event.get("metadata", {}).get("revision", "")
            
            # Shorten revision hash if it has @sha1:
            if "sha1:" in revision:
                revision_hash = revision.split("sha1:")[-1][:7]
            else:
                revision_hash = revision[:7]
                
            # Select tags based on severity
            tags = "information_source"
            if severity == "error":
                tags = "red_circle,warning"
            elif "succeeded" in message.lower() or "finished" in message.lower():
                tags = "green_circle,white_check_mark"
                
            # Format message
            msg_text = f"{message}\n\n"
            if revision_hash:
                msg_text += f"Revision: {revision_hash}"
                
            title = f"{kind} {namespace}/{name}"
            
            # Send to ntfy
            url = "https://ntfy.jw2.org/gitops"
            req_data = msg_text.encode('utf-8')
            
            req = urllib.request.Request(
                url, 
                data=req_data, 
                headers={
                    'Title': title,
                    'Tags': tags
                }
            )
            with urllib.request.urlopen(req) as response:
                pass
        except Exception as e:
            print(f"Error handling webhook: {e}")
            
        self.send_response(200)
        self.end_headers()

def run():
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(('', port), WebhookHandler)
    print(f"Starting ntfy bridge on port {port}...")
    server.serve_forever()

if __name__ == '__main__':
    run()
