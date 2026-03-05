# Clear the entire DB
docker compose exec web python manage.py shell -c "
from stores.models import StoreProduct
deleted, _ = StoreProduct.objects.all().delete()
print(f'Deleted {deleted} records')
"
# Test main.py 
docker compose exec web python /app/main.py

# Frontend - React/Vite UI
http://localhost:5173

# Backend API - DRF endpoints
http://localhost:8000/api/

# API Docs - Swagger UI
http://localhost:8000/api/docs/

# Admin - Django admin panel
http://localhost:8000/admin/

# Test root API (should return JSON now)
curl http://localhost:8000/api/
# 3. Test API responds
curl -s http://localhost:8000/api/ | python3 -m json.tool

# Test API docs (Swagger UI)
curl http://localhost:8000/api/docs/

# Test Django admin
curl -I http://localhost:8000/admin/

docker compose exec db psql -U postgres -d beer_near_here -c "\dt"

# Start DB
docker compose up -d db

# Backend build
docker compose up -d --build web
docker compose build up --build --no-cache web

# Frontend build
docker compose up -d --build react
docker compose build --no-cache react

# Start backend
docker compose up web
# Stop backend
docker compose stop web

# Start all services
docker compose up -d --buld
docker compose up -d

# Build all services
docker compose build
# Build everything
docker compose up -d

# Check backend logs
docker compose logs web

# Check database logs
docker compose logs db

# Check frontend logs
docker compose logs react

# Restart a single service
docker compose restart web

# Print project folder structure
tree -L 3 -I 'node_modules|.git|__pycache__|*.pyc|venv|dist|build' > project_structure.md

#NPM packages
https://www.npmjs.com/package/axios

# Stop existing containers
docker-compose down

# Build fresh
docker-compose build --no-cache

# Start services
docker-compose up -d

# Verify services
docker-compose ps

# Test database
docker-compose exec db psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "\dt"

# Test Walmart API
docker-compose exec web python manage.py shell
>>> from core.services.walmart import search_products
>>> search_products("beer", "90210")

# View logs if issues
docker-compose logs -f web

# 1. Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('docker-compose.yml'))" && echo "✅ docker-compose.yml valid"

# 2. Validate Dockerfile can build
docker build -t test-backend -f backend/Dockerfile ./backend && echo "✅ Dockerfile valid"

# 3. Test docker-compose config
docker-compose config > /dev/null && echo "✅ docker-compose config valid"

# 4. Full rebuild test
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 5. Verify all services running
docker-compose ps

# 6. Test backend
docker-compose exec web python -c "import django; print(f'Django {django.get_version()} ✅')"

# 7. Test Walmart API import
docker-compose exec web python -c "from cryptography.hazmat.primitives import hashes; print('✅ cryptography loaded')"

# Validate docker-compose.yml
docker-compose config > /dev/null && echo "✅ docker-compose.yml valid"

# Build all services
docker-compose build

# Start all services
docker-compose up -d

# Verify
docker-compose ps


# 1. On your EC2 instance:
git clone <your-repo>
cd beer-near-here

# 2. Copy your .env (or use AWS Parameter Store)
cp .env.example .env
# Edit .env with production values:
# - DJANGO_SECRET_KEY=secure-prod-key
# - DEBUG=False
# - DJANGO_ALLOWED_HOSTS=your-ec2-ip,localhost

# 3. Run the SAFE deployment script:
./scripts/deploy-ec2.sh

# 4. Verify:
docker compose ps
curl http://localhost:8000/api/


# Beer Near Here — Production Deployment Checklist

## 1. Environment (.env)
- [x ] Set `DEBUG=False`
- [x ] Generate and set a new `DJANGO_SECRET_KEY`
      ```bash
      python -c "import secrets; print(secrets.token_urlsafe(50))"
      ```
- [x ] Add EC2 IP/domain to `DJANGO_ALLOWED_HOSTS`
      ```
      DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,your-ec2-ip,your-domain.com
      ```

---

## 2. backend/config/settings.py
- [x ] Remove duplicate `DEBUG` definition (keep only one, after `BASE_DIR` and `SECRET_KEY`)
- [x ] Move security settings block to after `DEBUG` is defined
- [x ] Update `CORS_ALLOWED_ORIGINS` to include EC2 IP/domain or read from `.env`

---

## 3. Backend Files
- [x ] Add `auth_views.py` to `backend/stores/`
- [x ] Update `backend/stores/urls.py` with auth endpoints and `/products/` endpoint
- [x ] Update `backend/stores/views.py` with `IsAuthenticated` on both views
- [x ] Add `import requests` to top of `backend/stores/spiders/kroger.py` (remove from inside functions)
- [x ] Add `store_cache.json` to `.gitignore`
- [x ] Fix `search_fields` in `backend/stores/admin.py` → `('name', 'product_url')`

---

## 4. Frontend Files
- [x ] Add `frontend/src/context/AuthContext.jsx`
- [x ] Update `frontend/src/main.jsx` with `AuthProvider`
- [x ] Update `frontend/src/App.jsx` with protected routes
- [x ] Add `frontend/src/pages/AuthPage.jsx`
- [x ] Add `frontend/src/pages/AuthPage.module.css`
- [x ] Update `frontend/src/components/Nav.jsx` with sign out button
- [x ] Update `frontend/src/components/Nav.module.css`
- [x ] Update `frontend/index.html` title to `Beer Near Here` ✅
- [x ] Remove `esbuild` block from `vite.config.js`
- [x ] Remove `rewrite` from proxy in `vite.config.js` ✅

---

## 5. Docker — Production Setup
- [x ] Add `docker-compose.prod.yml` to project root
- [x ] Add `frontend/Dockerfile.prod` (multi-stage build)
- [x ] Verify `docker/nginx.conf` is in place ✅
- [x ] Update `backend/Dockerfile` — combine pip install lines, fix non-root username from `celeryuser` to `appuser`
- [x ] Update `frontend/Dockerfile` — already on `node:24.14.0-bookworm-slim` ✅

---

## 6. EC2 Server Setup
- [x ] Install Docker and Docker Compose on EC2
- [ ] Clone repo onto EC2
- [ ] Copy `.env` file to EC2 (never commit to git)
- [ ] Copy `certs/WM_IO_private_key.pem` to EC2
- [ ] Open ports 80 and 443 in EC2 security group
- [ ] Run `docker compose -f docker-compose.prod.yml up -d --build`
- [ ] Verify all 3 containers are running (`docker compose ps`)
- [ ] Run `docker compose exec web python manage.py createsuperuser`

---

## 7. Post-Deployment Verification
- [ ] Hit `http://your-ec2-ip` — should show login page
- [ ] Sign up and sign in successfully
- [ ] Run a beer search and verify results from both Kroger and Walmart
- [ ] Check history page shows saved products
- [ ] Hit `http://your-ec2-ip/admin/` — should show Django admin
- [ ] Check `docker compose logs web` for any errors

---

## 8. Optional / Future
- [ ] Add SSL/HTTPS via Let's Encrypt (Certbot)
- [ ] Add domain name via Route53
- [ ] Set `SECURE_HSTS_SECONDS` to a higher value (e.g. 31536000) after SSL is confirmed working
- [ ] Set up GitHub Actions CI/CD pipeline
- [ ] Add Sentry for error monitoring
- [ ] Move Walmart store cache from file to database
- [ ] Add Celery for background task processing (async API calls)