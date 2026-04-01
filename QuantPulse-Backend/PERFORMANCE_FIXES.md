# Performance & Timeout Issues - Analysis & Fixes

## Issues Identified from Render Logs (April 1, 2026)

### 1. LSTM Model Loading Blocks Everything (60+ seconds) ❌
**Problem:**
```
17:48:12 - First prediction request - loading LSTM model...
17:49:03 - LSTM model ready (51 seconds!)
```
- LSTM model download from Hugging Face takes 50-60 seconds
- Blocks ALL concurrent requests during this time
- Dashboard freezes completely

**Root Cause:**
- Model loading happens synchronously in the request handler
- No background task or startup preloading
- Every worker loads the model independently

**Solutions Implemented:**
1. ✅ Added better error logging with exception types
2. ✅ Added timeout warnings in frontend (120s for V2 analysis)
3. ✅ Added retry button for failed requests

**TODO (Backend Optimization):**
- [ ] Preload LSTM model during startup (not on first request)
- [ ] Use background task for model loading
- [ ] Add model loading status endpoint
- [ ] Implement request queuing during model load

### 2. IndianAPI Failures with Empty Error Messages ❌
**Problem:**
```
17:49:16 - ERROR - ❌ IndianAPI quote failed for RELIANCE:
(no actual error message!)
```

**Root Cause:**
- Exception logging was just `{e}` which can be empty
- No response body logging for HTTP errors
- No exception type logging

**Solutions Implemented:**
✅ Enhanced error logging in all providers:
```python
except Exception as e:
    logger.error(f"❌ Failed: {type(e).__name__}: {str(e)}")
```
✅ Added HTTP response body logging:
```python
except httpx.HTTPStatusError as e:
    error_body = e.response.text
    logger.error(f"❌ HTTP {e.response.status_code} - {error_body}")
```

### 3. Request Coalescing Causing Waits ⚠️
**Problem:**
```
17:49:12 - Coalescing request for key: stock_quote:RELIANCE
```
- Multiple requests for same stock are coalesced
- If first request is slow (60s), all others wait
- No timeout on coalesced requests

**Current Behavior:**
- Cache service coalesces duplicate requests
- Good for preventing API quota destruction
- Bad when first request is slow

**TODO (Optimization):**
- [ ] Add timeout to coalesced requests (30s max wait)
- [ ] Implement request priority (user-initiated vs background)
- [ ] Add circuit breaker for slow endpoints

### 4. Market Trending Endpoint Failing ❌
**Problem:**
```
17:49:16 - ERROR - ❌ Trending stocks fetch failed:Menu
```
Error message is just "Menu" - very strange!

**Possible Causes:**
- IndianAPI returning HTML error page instead of JSON
- Rate limiting or API key issues
- Parsing error in response handling

**Solutions Implemented:**
✅ Enhanced error logging with response body
✅ Increased timeout from 30s to 60s for trending endpoint
✅ Better exception type logging

### 5. Multiple Concurrent Requests Overwhelming Server ⚠️
**Problem:**
Dashboard makes 4-5 requests simultaneously:
1. `/api/market/trending` (slow)
2. `/stock/RELIANCE` (medium)
3. `/api/v2/analyze/NIFTY50` (very slow - 60s+)
4. `/api/portfolio/holdings` (fast)
5. `/api/auth/me` (fast)

**Impact:**
- Server with 1 worker gets overwhelmed
- Requests queue up
- Frontend appears frozen

**Solutions Implemented:**
✅ Added request timeouts in frontend:
- Health check: 5s
- Stock quotes: 15s
- Trending stocks: 15s
- V2 Analysis: 120s (LSTM loading)

✅ Added loading states and retry buttons
✅ Added timeout error messages

**TODO (Optimization):**
- [ ] Implement request prioritization
- [ ] Add request debouncing in frontend
- [ ] Use WebSocket for real-time updates
- [ ] Implement progressive loading (show data as it arrives)

## Performance Recommendations

### Immediate (High Priority)
1. **Preload LSTM Model on Startup**
   ```python
   @app.on_event("startup")
   async def startup_event():
       # ... existing code ...
       
       # Preload LSTM model in background
       from app.services.lstm_service import lstm_service
       asyncio.create_task(lstm_service.preload_model())
   ```

2. **Add Model Loading Status Endpoint**
   ```python
   @router.get("/api/v2/model-status")
   async def get_model_status():
       return {
           "lstm_loaded": lstm_service.is_loaded(),
           "loading": lstm_service.is_loading(),
           "load_time": lstm_service.load_time
       }
   ```

3. **Implement Request Queuing**
   - Queue V2 analysis requests during model load
   - Return 202 Accepted with retry-after header
   - Frontend polls for results

### Short Term (Medium Priority)
1. **Add Circuit Breaker**
   - Detect slow/failing endpoints
   - Temporarily disable to prevent cascading failures
   - Auto-recover after cooldown period

2. **Implement Request Caching**
   - Cache V2 analysis results for 5-10 minutes
   - Serve cached results immediately
   - Update cache in background

3. **Add Request Prioritization**
   - User-initiated requests get priority
   - Background/prefetch requests are queued
   - Implement fair queuing algorithm

### Long Term (Low Priority)
1. **Use Redis for Distributed Caching**
   - Share cache across multiple workers
   - Persistent cache survives restarts
   - Pub/sub for cache invalidation

2. **Implement WebSocket Updates**
   - Real-time price updates
   - Push notifications for analysis completion
   - Reduce polling overhead

3. **Add CDN for Static Assets**
   - Cache LSTM model on CDN
   - Faster model downloads
   - Reduce Hugging Face API calls

## Testing Checklist

### Before Deployment
- [ ] Test LSTM model loading on cold start
- [ ] Test concurrent requests (10+ simultaneous)
- [ ] Test timeout handling in frontend
- [ ] Test error recovery and retry logic
- [ ] Test with slow network (throttle to 3G)
- [ ] Test with API failures (mock 500 errors)

### After Deployment
- [ ] Monitor LSTM load times
- [ ] Monitor request queue lengths
- [ ] Monitor timeout rates
- [ ] Monitor error rates by endpoint
- [ ] Monitor cache hit rates

## Monitoring Metrics to Add

1. **Request Metrics**
   - Request duration by endpoint
   - Request queue length
   - Concurrent request count
   - Timeout rate

2. **Model Metrics**
   - LSTM load time
   - LSTM inference time
   - Model cache hit rate
   - Model memory usage

3. **API Metrics**
   - IndianAPI response time
   - IndianAPI error rate
   - yfinance response time
   - yfinance error rate

4. **Cache Metrics**
   - Cache hit rate by type
   - Cache size
   - Cache eviction rate
   - Coalesced request count

---

**Status**: Error logging improved ✅
**Next**: Implement LSTM preloading and request queuing
**Priority**: High - Affects user experience significantly
