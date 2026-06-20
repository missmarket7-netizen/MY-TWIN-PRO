# MyTwin – Disaster Recovery Plan

## Supabase Falls
1. Switch to Supabase backup project (secondary instance)
2. Restore from daily backup (available in Supabase dashboard)
3. Update SUPABASE_URL in Railway environment variables
4. Deploy immediately

## Gemini API Falls
1. Groq automatically takes over via Load Balancer
2. OpenRouter serves as fallback
3. Admin panel shows "Gemini: DOWN"

## OpenRouter Falls
1. Groq + Gemini handle all traffic
2. Admin panel shows "OpenRouter: DOWN"

## Railway Falls
1. Railway auto-restarts (ON_FAILURE policy)
2. Secondary Railway instance in different region
3. DNS failover to secondary instance

## Backup Schedule
- Database: Daily automated backups (Supabase)
- Code: GitHub (every push)
- Environment: Railway environment variables (export weekly)

## Restore Time
- Database: < 15 minutes
- Code: < 5 minutes (git push)
- Full system: < 30 minutes
