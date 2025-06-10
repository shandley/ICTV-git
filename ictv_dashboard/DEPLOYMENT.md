# ICTV Dashboard Deployment Guide

## 🚀 Streamlit Cloud Deployment (Recommended)

### Prerequisites
- GitHub account
- Streamlit Cloud account (free at share.streamlit.io)
- This repository pushed to GitHub

### Step 1: Prepare Repository

1. **Ensure all files are committed**
   ```bash
   git add .
   git commit -m "Prepare for Streamlit Cloud deployment"
   git push origin main
   ```

2. **Verify required files exist**
   - `requirements.txt` - Python dependencies ✓
   - `.streamlit/config.toml` - App configuration ✓
   - `app.py` - Main application file ✓

### Step 2: Deploy to Streamlit Cloud

1. **Go to [share.streamlit.io](https://share.streamlit.io)**

2. **Click "New app"**

3. **Configure deployment**:
   - Repository: `your-github-username/ICTV-git`
   - Branch: `main`
   - Main file path: `ictv_dashboard/app.py`

4. **Advanced settings**:
   - Python version: 3.9 (or latest)
   - Add any secrets/environment variables if needed

5. **Click "Deploy"**

### Step 3: Access Your App

- Your app will be available at: `https://your-app-name.streamlit.app`
- First deployment may take 2-5 minutes
- Subsequent updates are faster

### Step 4: Custom Domain (Optional)

1. In Streamlit Cloud dashboard, go to Settings
2. Add custom domain (e.g., `ictv-dashboard.yourdomain.org`)
3. Update DNS records as instructed

## 🔐 Authentication

The dashboard includes basic password protection:

### Default Credentials
- **Demo Access**: Password: `demo123`
- **Committee Access**: Password: `ictv2025`
- **Admin Access**: Password: `admin2025`

### To Change Passwords

1. Edit `utils/authentication.py`
2. Update the `DEMO_PASSWORDS` dictionary
3. Commit and push changes

### For Production

Consider implementing:
- Environment variables for passwords
- OAuth integration
- Database-backed user management
- Session timeout

## 🐳 Docker Deployment (Alternative)

### Create Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Build and Run

```bash
docker build -t ictv-dashboard .
docker run -p 8501:8501 ictv-dashboard
```

## 🛠️ Troubleshooting

### Common Issues

1. **Import errors**
   - Ensure all file paths are relative
   - Check `sys.path` additions in app.py

2. **Missing dependencies**
   - Update requirements.txt
   - Clear Streamlit Cloud cache

3. **Authentication not working**
   - Check session state initialization
   - Verify password hashing

### Performance Optimization

1. **Enable caching**
   ```python
   @st.cache_data
   def load_data():
       # Your data loading code
   ```

2. **Optimize data loading**
   - Use lightweight sample data
   - Implement pagination for large datasets

3. **Reduce plot complexity**
   - Limit number of data points
   - Use sampling for large visualizations

## 📊 Monitoring

### Streamlit Cloud Analytics
- View app metrics in dashboard
- Monitor user engagement
- Track performance issues

### Add Custom Analytics
```python
# In app.py
import os
if os.getenv("ANALYTICS_ENABLED"):
    # Add analytics code
    pass
```

## 🔄 Updates and Maintenance

### Updating the App

1. Make changes locally
2. Test thoroughly
3. Commit and push to GitHub
4. Streamlit Cloud auto-deploys

### Version Management

Tag releases for easy rollback:
```bash
git tag -a v1.0.0 -m "Initial deployment"
git push origin v1.0.0
```

## 📞 Support

### For ICTV Committee
- Technical issues: [create issue on GitHub]
- Access requests: [contact admin]
- Feature requests: [use dashboard feedback form]

### Resources
- [Streamlit Documentation](https://docs.streamlit.io)
- [Deployment Best Practices](https://docs.streamlit.io/streamlit-cloud/deploy)
- [Security Guidelines](https://docs.streamlit.io/streamlit-cloud/trust-and-security)

---

*Deployment guide for ICTV Interactive Dashboard v1.0*
*Last updated: January 2025*