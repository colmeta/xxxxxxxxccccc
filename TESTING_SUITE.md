# Pearl Data Intelligence - Test Suite 🔬

## Overview
Sophisticated test commands to validate platform stability, performance, and edge case handling.

## 1️⃣ Concurrency Stress Tests
**Goal**: Test simultaneous job handling capacity

### Via Oracle (Natural Language)
```
Find me 50 different cybersecurity CEOs across Austin, Seattle, Denver, Portland, Boston, Miami, Atlanta, Chicago, Dallas, Phoenix
```

### Via Direct API (Bulk)
```bash
curl -X POST https://your-api.com/api/v1/jobs/bulk \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"queries": ["DevOps Engineers in SF", "PMs in NYC", ...], "platform": "linkedin"}'
```

**Expected**: ✅ Sequential processing without crashes | ❌ Crashes or locks

## 2️⃣ Scraper Stress Tests
**Goal**: Test scraper reliability and breaking points

### LinkedIn - Obscure Queries
- Quantum Computing researchers in Antarctica
- Professional unicorn trainers in Silicon Valley
- Time travel consultants in Tokyo

### Google Maps - High Volume
- Find all coffee shops in Manhattan
- Find all restaurants in Los Angeles

### Multi-Platform Cascade
Find ethical hackers in Edmonton on: LinkedIn, Google Maps, Twitter, Instagram, Company Websites

**Expected**: ✅ Results or graceful empty | ❌ Crashes or infinite loops

## 3️⃣ AI System Challenges
**Goal**: Test AI fallback mechanisms

### Gemini Quota Exhaustion
Run 1000+ queries rapidly to exhaust API quota

### Complex Arbiter Scoring
Find profiles: Series B funded, 50-200 employees, expanding to Europe, tech stack Python/React/AWS, hiring VP Sales

**Expected**: ✅ Falls back to heuristic intelligence | ❌ Jobs stuck or null scores

## 4️⃣ Data Vault Tests
**Goal**: Test vault architecture and de-duplication

### Duplicate Detection
Submit same query 10x: "Find Elon Musk on LinkedIn"

### Vault Leverage Test
1. Find Mark Zuckerberg (fresh scrape)
2. Find Mark Zuckerberg 5 mins later (should use vault)

**Expected**: ✅ Second query faster via vault | ❌ Re-scrapes

## 5️⃣ Edge Case Queries
**Goal**: Test unusual inputs

### Special Characters
- O'Reilly Media employees in Sebastopol
- Companies: C++, .NET, R&D
- Profiles with emojis: 🚀 Startup Founder

### Invalid Inputs
- Empty query: ""
- Null platform
- 10k character query
- Invalid platforms: myspace, friendster

**Expected**: ✅ Validation errors | ❌ Crashes

## 6️⃣ Compliance & Security
**Goal**: Verify opt-out and RLS policies

### Opt-Out Enforcement
```sql
INSERT INTO opt_out_registry (identifier_hash)
VALUES (encode(digest('test@blocked.com', 'sha256'), 'hex'));
```
Then try scraping that email

**Expected**: ✅ Opted-out contacts scrubbed | ❌ Returns sensitive data

## 7️⃣ Enrichment Bridge
**Goal**: Test business-to-person enrichment

### Google Maps → LinkedIn
Find cybersecurity companies in Austin → Should enrich with employee contacts

**Expected**: ✅ Enriches with people data | ❌ Only business info

## 8️⃣ Resource Exhaustion
**Goal**: Find memory leaks

### Browser Instance Leak
Run 100 consecutive jobs, monitor memory with `watch -n 1 'ps aux | grep hydra'`

**Expected**: ✅ Memory stable | ❌ Memory grows continuously

## 9️⃣ Stealth & Anti-Detection
**Goal**: Test blocking avoidance

### Rapid-Fire Requests
100 LinkedIn queries in 60 seconds

### Geographic Distribution
Run 50 searches, verify different IPs in `worker_status.public_ip`

**Expected**: ✅ Rotates UAs, uses proxies | ❌ Gets blocked

## 🔟 Performance Benchmarks
**Goal**: Measure speed and throughput

### Single Job Latency
```bash
time curl -X POST https://your-api.com/api/v1/jobs \
  -d '{"query": "SaaS CEOs in Austin", "platform": "linkedin"}' \
  -w "\nTotal Time: %{time_total}s\n"
```

### Throughput
```sql
SELECT COUNT(*) FROM jobs 
WHERE status = 'completed' AND completed_at > NOW() - INTERVAL '1 hour';
```

**Targets**: Single job < 30s, Throughput > 100 jobs/hr, Success rate > 95%

## 📊 Monitoring Queries

### Overall Health
```sql
SELECT status, COUNT(*) as count,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM jobs WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY status;
```

### Worker Performance
```sql
SELECT worker_id, stealth_health, active_missions, geo_city, last_pulse
FROM worker_status WHERE last_pulse > NOW() - INTERVAL '5 minutes';
```

### Data Quality
```sql
SELECT 
  CASE WHEN clarity_score >= 80 THEN 'High (80-100)'
       WHEN clarity_score >= 50 THEN 'Medium (50-79)'
       ELSE 'Low (0-49)' END as quality,
  COUNT(*) as count
FROM results WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY quality;
```

### Vault Efficiency
```sql
SELECT 
  COUNT(CASE WHEN data_payload->>'vault_leverage' = 'true' THEN 1 END) as vault_hits,
  COUNT(*) as total,
  ROUND(COUNT(CASE WHEN data_payload->>'vault_leverage' = 'true' THEN 1 END) * 100.0 / COUNT(*), 2) as hit_rate_pct
FROM results WHERE created_at > NOW() - INTERVAL '24 hours';
```

## 🚨 Failure Scenarios
1. Database Connection Loss - Queue locally or fail gracefully
2. Proxy Pool Exhaustion - Fall back to direct
3. AI Service Complete Failure - Use heuristics 100%
4. Browser Launch Failure - Log error, mark job failed

## 🎯 Test Sequence
1. **Phase 1 (Week 1)**: 10 normal queries, baseline metrics
2. **Phase 2 (Week 2)**: Scale to 100 jobs/day, monitor resources
3. **Phase 3 (Week 3)**: Concurrency tests, edge cases, failures
4. **Phase 4 (Week 4)**: 24/7 endurance, check for leaks

## 📈 Success Criteria
| Metric | Target | Critical |
|--------|--------|----------|
| Job Success Rate | > 95% | < 80% |
| Avg Completion | < 30s | > 60s |
| Memory Usage | < 2GB | > 4GB |
| API Error Rate | < 5% | > 20% |
| Vault Hit Rate | > 30% | < 10% |
| Worker Uptime | > 99% | < 95% |

## 🛠️ Debugging Commands

### View Recent Errors
```sql
SELECT job_id, error_log, created_at 
FROM jobs WHERE status = 'failed' 
ORDER BY created_at DESC LIMIT 20;
```

### Check Stuck Jobs
```sql
SELECT id, target_query, started_at 
FROM jobs WHERE status = 'running' 
AND started_at < NOW() - INTERVAL '10 minutes';
```

### Audit Compliance
```sql
SELECT COUNT(*) as opted_out_scraped
FROM results r JOIN jobs j ON r.job_id = j.id
WHERE r.data_payload->>'status' = 'scrubbed';
```

## 💡 Testing Tips
- Start small, test one category at a time
- Document all failures with timestamps
- Use staging first, never stress production
- Monitor real-time with logs/dashboards
- Have rollback ready
- Test in waves
