from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

@app.post("/test/frame")
async def test_frame_upload(request: Request):
    try:
        print(f"[TEST] Content-Type: {request.headers.get('content-type')}")
        
        # Try to read raw body
        raw_body = await request.body()
        print(f"[TEST] Raw body size: {len(raw_body)} bytes")
        
        # Try to parse form data
        form = await request.form()
        print(f"[TEST] Form keys: {list(form.keys())}")
        
        file = form.get("file")
        if file:
            content = await file.read()
            print(f"[TEST] File content size: {len(content)} bytes")
            return {"status": "success", "size": len(content)}
        else:
            return {"status": "no file found"}
            
    except Exception as e:
        print(f"[TEST] Error: {e}")
        import traceback
        print(f"[TEST] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8002)