"""Simple load test for MyTwin API."""
import asyncio, httpx, time, sys

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
CONCURRENT = int(sys.argv[2]) if len(sys.argv) > 2 else 10
REQUESTS = int(sys.argv[3]) if len(sys.argv) > 3 else 100

async def test_endpoint(client, path):
    try:
        resp = await client.get(f"{BASE}{path}", timeout=5)
        return resp.status_code
    except:
        return 0

async def main():
    start = time.time()
    async with httpx.AsyncClient() as client:
        tasks = []
        for _ in range(REQUESTS):
            tasks.append(test_endpoint(client, "/health"))
        results = await asyncio.gather(*tasks)
    
    ok = sum(1 for r in results if r == 200)
    fail = len(results) - ok
    elapsed = time.time() - start
    
    print(f"📊 Results: {ok} OK, {fail} FAIL in {elapsed:.1f}s")
    print(f"   Rate: {len(results)/elapsed:.1f} req/s")
    print(f"   Success: {ok/len(results)*100:.1f}%")

asyncio.run(main())
