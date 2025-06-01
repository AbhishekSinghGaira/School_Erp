# Deploying to PythonAnywhere

## 1. Prepare your code
- Make sure your settings.py has:
  - `DEBUG = False`
  - Your PythonAnywhere domain in `ALLOWED_HOSTS`
  - `STATIC_ROOT` set (e.g. `BASE_DIR / 'staticfiles'`)
- All dependencies listed in `requirements.txt`

## 2. Upload your code to PythonAnywhere
- You can use Git, or upload a zip and extract it.

## 3. Set up a virtualenv on PythonAnywhere
```
mkvirtualenv myenv --python=python3.10
pip install -r requirements.txt
```

## 4. Set up the WSGI file
- Point it to your project's `wsgi.py` (e.g. `/home/yourusername/yourproject/school_erp/wsgi.py`)

## 5. Migrate the database
```
python manage.py migrate
```

## 6. Collect static files
```
python manage.py collectstatic
```
- On PythonAnywhere, set up a static files mapping:
  - URL: `/static/` → Directory: `/home/yourusername/yourproject/staticfiles/`
  - URL: `/media/` → Directory: `/home/yourusername/yourproject/media/`

## 7. Reload your web app
- Use the PythonAnywhere web interface to reload your app after changes.

## 8. (Optional) Set up a custom domain and HTTPS
- Follow PythonAnywhere's docs for custom domains and SSL.

---
**Tip:** Never commit your real SECRET_KEY or production passwords to public repos! 