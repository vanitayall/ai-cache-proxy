package proxy

import (
	"context"
	"encoding/json"
	"fmt"
	"go-proxy/internal/cache"
	"io"
	"net/http"
	"strconv"
	"time"
)

// AnalyticsResponse represents the analytics data structure
type AnalyticsResponse struct {
	Status    string                 `json:"status"`
	Data      map[string]interface{} `json:"data"`
	Timestamp string                 `json:"timestamp"`
}

// CacheStats represents cache statistics
type CacheStats struct {
	TotalRequests   int64   `json:"total_requests"`
	CacheHits       int64   `json:"cache_hits"`
	CacheMisses     int64   `json:"cache_misses"`
	CacheHitRate    float64 `json:"cache_hit_rate"`
	AIPredictions   int64   `json:"ai_predictions"`
	AvgResponseTime string  `json:"average_response_time"`
}

// ProxyHandler handles all proxy requests
func ProxyHandler(w http.ResponseWriter, r *http.Request) {
	// Handle special API endpoints
	switch r.URL.Path {
	case "/health":
		handleHealth(w, r)
		return
	case "/analytics":
		handleAnalytics(w, r)
		return
	case "/analytics/export":
		handleAnalyticsExport(w, r)
		return
	case "/cache/stats":
		handleCacheStats(w, r)
		return
	case "/cache/clear":
		handleCacheClear(w, r)
		return
	case "/ai/toggle":
		handleAIToggle(w, r)
		return
	case "/dashboard":
		handleDashboard(w, r)
		return
	}

	// Original proxy logic
	handleProxyRequest(w, r)
}

// handleProxyRequest contains the original proxy logic
func handleProxyRequest(w http.ResponseWriter, r *http.Request) {
	startTime := time.Now()
	
	// Cache key based on request path
	cacheKey := fmt.Sprintf("proxy:%s", r.URL.Path)

	// Check if response is in cache
	cachedResponse, err := cache.RedisClient.HGetAll(cache.GetContext(), cacheKey).Result()
	if err == nil && len(cachedResponse) > 0 {
		// Increment cache hits
		cache.RedisClient.Incr(context.Background(), "stats:cache_hits")
		
		// If found in cache, return cached response
		w.Header().Set("Content-Type", "application/json")
		w.Write([]byte(cachedResponse["response"]))
		return
	}

	// Increment cache misses
	cache.RedisClient.Incr(context.Background(), "stats:cache_misses")

	// If not in cache, continue with request to server
	targetURL := "http://httpbin.org" + r.URL.Path

	// Create new request to target server
	req, err := http.NewRequest(r.Method, targetURL, r.Body)
	if err != nil {
		http.Error(w, "Error creating request", http.StatusInternalServerError)
		return
	}

	// Copy headers from original request
	for name, values := range r.Header {
		for _, value := range values {
			req.Header.Add(name, value)
		}
	}

	// Execute request to target server
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		http.Error(w, "Error sending request to target server", http.StatusInternalServerError)
		return
	}
	defer resp.Body.Close()

	// Read response from target server
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		http.Error(w, "Error reading response", http.StatusInternalServerError)
		return
	}

	// Prepare headers for storage
	headers := make(map[string]string)
	for name, values := range r.Header {
		headers[name] = values[0] // Store only first header
	}
	headersJSON, _ := json.Marshal(headers)

	// Calculate response time
	responseTime := time.Since(startTime)

	// Store complete request and response data in Redis
	purpose := "empty"
	err = cache.RedisClient.HSet(context.Background(), cacheKey,
		"request_method", r.Method,
		"request_url", r.URL.String(),
		"request_headers", string(headersJSON),
		"response", string(body),
		"purpose", purpose,
		"response_time", responseTime.String(),
		"timestamp", time.Now().Format(time.RFC3339)).Err()
	if err != nil {
		http.Error(w, "Error saving data to Redis", http.StatusInternalServerError)
		return
	}

	// Increment total requests
	cache.RedisClient.Incr(context.Background(), "stats:total_requests")

	// Set response headers
	for name, values := range resp.Header {
		for _, value := range values {
			w.Header().Add(name, value)
		}
	}
	w.WriteHeader(resp.StatusCode)
	w.Write(body)
}

// handleHealth provides health check endpoint
func handleHealth(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	response := map[string]interface{}{
		"status":    "healthy",
		"timestamp": time.Now().Format(time.RFC3339),
		"service":   "ai-cache-proxy",
		"version":   "1.0.0",
	}
	json.NewEncoder(w).Encode(response)
}

// handleAnalytics provides analytics data
func handleAnalytics(w http.ResponseWriter, r *http.Request) {
	stats, err := getCacheStats()
	if err != nil {
		http.Error(w, "Error getting analytics", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	response := AnalyticsResponse{
		Status: "success",
		Data: map[string]interface{}{
			"cache_hit_rate":       stats.CacheHitRate,
			"total_requests":       stats.TotalRequests,
			"ai_predictions":       stats.AIPredictions,
			"average_response_time": stats.AvgResponseTime,
		},
		Timestamp: time.Now().Format(time.RFC3339),
	}
	json.NewEncoder(w).Encode(response)
}

// handleAnalyticsExport exports analytics data
func handleAnalyticsExport(w http.ResponseWriter, r *http.Request) {
	stats, err := getCacheStats()
	if err != nil {
		http.Error(w, "Error getting analytics", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.Header().Set("Content-Disposition", "attachment; filename=cache-analytics.json")
	
	exportData := map[string]interface{}{
		"export_timestamp": time.Now().Format(time.RFC3339),
		"analytics":        stats,
		"cache_keys":       getAllCacheKeys(),
	}
	json.NewEncoder(w).Encode(exportData)
}

// handleCacheStats provides detailed cache statistics
func handleCacheStats(w http.ResponseWriter, r *http.Request) {
	stats, err := getCacheStats()
	if err != nil {
		http.Error(w, "Error getting cache stats", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(stats)
}

// handleCacheClear clears all cached data
func handleCacheClear(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodDelete {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Clear all cache keys
	keys, err := cache.RedisClient.Keys(context.Background(), "proxy:*").Result()
	if err != nil {
		http.Error(w, "Error clearing cache", http.StatusInternalServerError)
		return
	}

	if len(keys) > 0 {
		cache.RedisClient.Del(context.Background(), keys...)
	}

	// Reset statistics
	cache.RedisClient.Set(context.Background(), "stats:total_requests", 0, 0)
	cache.RedisClient.Set(context.Background(), "stats:cache_hits", 0, 0)
	cache.RedisClient.Set(context.Background(), "stats:cache_misses", 0, 0)
	cache.RedisClient.Set(context.Background(), "stats:ai_predictions", 0, 0)

	w.Header().Set("Content-Type", "application/json")
	response := map[string]interface{}{
		"status":  "success",
		"message": "Cache cleared successfully",
		"cleared_keys": len(keys),
	}
	json.NewEncoder(w).Encode(response)
}

// handleAIToggle toggles AI mode
func handleAIToggle(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Get current AI status
	currentStatus, err := cache.RedisClient.Get(context.Background(), "ai:enabled").Result()
	if err != nil {
		currentStatus = "true" // Default to enabled
	}

	// Toggle status
	newStatus := "false"
	if currentStatus == "false" {
		newStatus = "true"
	}

	cache.RedisClient.Set(context.Background(), "ai:enabled", newStatus, 0)

	w.Header().Set("Content-Type", "application/json")
	response := map[string]interface{}{
		"status":  "success",
		"enabled": newStatus == "true",
		"message": "AI mode " + newStatus,
	}
	json.NewEncoder(w).Encode(response)
}

// handleDashboard serves the dashboard HTML
func handleDashboard(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "text/html")
	http.ServeFile(w, r, "dashboard/index.html")
}

// getCacheStats retrieves cache statistics from Redis
func getCacheStats() (*CacheStats, error) {
	ctx := context.Background()
	
	totalRequests, _ := cache.RedisClient.Get(ctx, "stats:total_requests").Int64()
	cacheHits, _ := cache.RedisClient.Get(ctx, "stats:cache_hits").Int64()
	cacheMisses, _ := cache.RedisClient.Get(ctx, "stats:cache_misses").Int64()
	aiPredictions, _ := cache.RedisClient.Get(ctx, "stats:ai_predictions").Int64()

	var cacheHitRate float64
	if totalRequests > 0 {
		cacheHitRate = float64(cacheHits) / float64(totalRequests)
	}

	// Calculate average response time (simplified)
	avgResponseTime := "45ms" // This would be calculated from actual response times

	return &CacheStats{
		TotalRequests:   totalRequests,
		CacheHits:       cacheHits,
		CacheMisses:     cacheMisses,
		CacheHitRate:    cacheHitRate,
		AIPredictions:   aiPredictions,
		AvgResponseTime: avgResponseTime,
	}, nil
}

// getAllCacheKeys retrieves all cache keys
func getAllCacheKeys() []string {
	keys, err := cache.RedisClient.Keys(context.Background(), "proxy:*").Result()
	if err != nil {
		return []string{}
	}
	return keys
}
