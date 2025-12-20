# ✅ Production Readiness Checklist

## 🎯 Overview

This checklist ensures your Hospitality AI Agent is ready for real restaurant owners to use.

**Goal:** Launch MVP in 3-4 weeks

---

## 🔴 **CRITICAL (Must Have Before Launch)**

### Business Logic (Agent Core)

#### KPI Calculations
- [ ] **Labor Cost %** calculation is accurate
  - File: `apps/agent_core/tasks/kpi_utils.py`
  - Test with real restaurant data
  - Verify: `(labor_cost / total_sales) * 100`

- [ ] **Food Cost %** calculation is accurate
  - Test with multiple scenarios
  - Handle edge cases (zero sales, negative values)

- [ ] **Prime Cost** calculation is accurate
  - Formula: `labor_cost + food_cost`
  - Percentage: `(prime_cost / total_sales) * 100`

- [ ] **Sales per Labor Hour** is accurate
  - Formula: `total_sales / hours_worked`
  - Handle zero hours edge case

#### Product Mix Analysis
- [ ] **Contribution Margin** calculated correctly
  - File: `apps/agent_core/tasks/menu/product_mix.py`
  - Formula: `price - cost`

- [ ] **Total Profit** per item calculated
  - Formula: `contribution_margin * quantity_sold`

- [ ] **Menu item ranking** works
  - Sort by profit margin
  - Identify stars vs dogs

#### API Endpoints
- [ ] `/api/kpi/summary/` returns valid JSON
  - Test POST request
  - Validate response format
  - Handle missing fields gracefully

- [ ] `/api/pmix/report/` works correctly
  - Test with sample data
  - Verify calculations match manual calculation

- [ ] Error responses are helpful
  - Return clear error messages
  - Use proper HTTP status codes (400, 500, etc.)

#### Data Validation
- [ ] All API endpoints validate input
  - Check required fields exist
  - Validate data types (numbers are numbers)
  - Check for negative values where inappropriate

- [ ] Handle edge cases
  - Zero sales
  - Missing data fields
  - Extremely large/small numbers

#### Error Handling
- [ ] Try-except blocks in all calculations
  - Don't crash on bad input
  - Return user-friendly error messages
  - Log errors for debugging

---

### Security

- [ ] `DEBUG = False` in production
  - Update `config/settings.py`
  - Use environment variable

- [ ] `SECRET_KEY` from environment variable
  - Never commit to git
  - Use strong random string

- [ ] `ALLOWED_HOSTS` configured
  - Add your domain
  - Add AWS domain

- [ ] Database credentials secure
  - Use environment variables
  - Not in code or git

- [ ] HTTPS enabled
  - SSL certificate installed
  - Redirect HTTP to HTTPS

- [ ] CORS configured properly
  - Only allow trusted domains
  - Not `CORS_ALLOW_ALL_ORIGINS = True` in production

---

### Database

- [ ] Migrations created and tested
  - Run `python manage.py makemigrations`
  - Run `python manage.py migrate`
  - Test rollback if needed

- [ ] Database backups configured
  - AWS RDS automatic backups
  - Or manual backup script

- [ ] Production database chosen
  - PostgreSQL recommended
  - Not SQLite for production

---

### Performance

- [ ] Static files collected
  - Run `python manage.py collectstatic`
  - Verify static files load

- [ ] Gunicorn configured (not Django dev server)
  - Use multiple workers
  - Configure timeouts

- [ ] Database queries optimized
  - Use `select_related()` where appropriate
  - Avoid N+1 queries

---

## 🟡 **IMPORTANT (Should Have Soon)**

### Testing

- [ ] Unit tests for core calculations
  - File: `tests/unit/test_kpi.py`
  - Test each KPI formula
  - Test edge cases

- [ ] Integration tests for API endpoints
  - File: `tests/integration/test_api.py`
  - Test full request/response cycle

- [ ] Test coverage > 70%
  - Run `coverage run manage.py test`
  - Run `coverage report`

### UI/UX

- [ ] All pages mobile-responsive
  - Test on real phone
  - Use Chrome DevTools mobile view

- [ ] Loading states added
  - Show spinner during API calls
  - Disable buttons while loading

- [ ] Error messages user-friendly
  - No technical jargon
  - Suggest solutions

- [ ] Empty states handled
  - Show helpful message when no data
  - Suggest next action

### Monitoring

- [ ] Error logging configured
  - Use Sentry or similar
  - Get notifications for errors

- [ ] Performance monitoring
  - Track response times
  - Monitor database queries

- [ ] Uptime monitoring
  - Use UptimeRobot or similar
  - Get alerts if site goes down

---

## 🟢 **NICE TO HAVE (Polish)**

### Features

- [ ] PDF export functionality
  - Export reports to PDF
  - Include charts and tables

- [ ] Email notifications
  - Alert when KPIs exceed thresholds
  - Daily/weekly reports

- [ ] Data export (CSV/Excel)
  - Export raw data
  - For external analysis

- [ ] User authentication
  - Login/logout
  - Multiple users per restaurant
  - Role-based permissions

### UI Polish

- [ ] Animations smooth
  - Page transitions
  - Chart animations
  - Hover effects

- [ ] Design system fully applied
  - All pages consistent
  - Colors match brand
  - Typography consistent

- [ ] Dark mode
  - Toggle in settings
  - Saves user preference

### Documentation

- [ ] API documentation
  - Document all endpoints
  - Include examples
  - Use Swagger/OpenAPI

- [ ] User guide
  - How to use each feature
  - Screenshots
  - Common workflows

- [ ] Admin guide
  - How to manage users
  - How to troubleshoot
  - Backup/restore procedures

---

## 📋 **Quick Start: First 3 Weeks**

### Week 1: Core Logic
```
Day 1-2: Fix KPI calculations
  - Test all formulas manually
  - Add validation
  - Handle edge cases

Day 3-4: Complete API endpoints
  - Test all endpoints
  - Add error handling
  - Write basic tests

Day 5: Security basics
  - Environment variables
  - ALLOWED_HOSTS
  - DEBUG = False
```

### Week 2: Deploy to AWS
```
Day 1-2: Set up AWS
  - Create EC2 or EB
  - Set up database
  - Configure domain

Day 3: Deploy app
  - Push code
  - Run migrations
  - Collect static files

Day 4-5: Test in production
  - Test all features
  - Fix any issues
  - Monitor errors
```

### Week 3: Essential Polish
```
Day 1-2: Fix critical UI issues
  - Mobile responsiveness
  - Loading states
  - Error messages

Day 3-4: Add monitoring
  - Error tracking
  - Performance monitoring
  - Uptime monitoring

Day 5: Documentation
  - User guide basics
  - API docs
  - Deployment notes
```

---

## 🎯 **MVP Launch Criteria**

Your app is ready to launch when:

1. ✅ Core KPI calculations work correctly
2. ✅ API endpoints return valid data
3. ✅ App is deployed and accessible
4. ✅ HTTPS is working
5. ✅ No critical bugs
6. ✅ Basic error handling exists
7. ✅ Works on mobile
8. ✅ You've tested with real data

**Don't wait for perfection!** Launch when these 8 criteria are met, then iterate.

---

## 🚨 **Common Mistakes to Avoid**

❌ **Perfectionism**
- Don't spend 6 months building features
- Launch MVP in 3-4 weeks
- Iterate based on user feedback

❌ **Premature Optimization**
- Don't optimize before you have users
- Focus on correctness first
- Optimize when you have real performance data

❌ **Over-Engineering**
- Don't build features users don't need
- Start simple
- Add complexity only when necessary

❌ **Ignoring Security**
- Never deploy without HTTPS
- Never hardcode secrets
- Always validate user input

---

## 📊 **Progress Tracking**

Update this checklist as you complete items:

**Core Logic:** __ / 15 items complete
**Security:** __ / 6 items complete
**Database:** __ / 3 items complete
**Performance:** __ / 3 items complete

**TOTAL CRITICAL:** __ / 27 items (Need 100% before launch)

---

## 🆘 **Need Help?**

If you're stuck on any item:

1. **Business Logic Issues:**
   - Review calculation formulas
   - Test with sample data
   - Ask for code review

2. **Deployment Issues:**
   - Check AWS_DEPLOYMENT.md guide
   - Review error logs
   - Test locally first

3. **UI/UX Issues:**
   - Check DESIGN_SYSTEM.md
   - Test on real devices
   - Get user feedback

---

**Remember:** Done is better than perfect. Ship MVP, then iterate! 🚀
