# 🚀 Deployment Guide - Team Tools Calculator

Your calculator is ready to deploy online! Here are several free deployment options:

## 🎯 Quick Deploy Options

### 1. **Railway** (Recommended - Already Configured!)
✅ **Easy**: One-click deployment
✅ **Free**: Generous free tier
✅ **Fast**: Deploys in 2-3 minutes

**Steps:**
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "Deploy from GitHub repo"
4. Select your `team-tools` repository
5. Railway will automatically detect and deploy!

**Your calculator will be live at:** `https://your-app-name.railway.app`

### 2. **Render** (Also Great!)
✅ **Free**: No credit card required
✅ **Simple**: GitHub integration
✅ **Reliable**: Good uptime

**Steps:**
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Click "New Web Service"
4. Connect your `team-tools` repository
5. Render will use the `render.yaml` configuration automatically

### 3. **Vercel** (For Static-Like Apps)
✅ **Fast**: Global CDN
✅ **Free**: Generous limits
✅ **Simple**: Git integration

**Steps:**
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Click "New Project"
4. Import your `team-tools` repository
5. Vercel will use the `vercel.json` configuration

### 4. **Heroku** (Classic Option)
✅ **Established**: Been around forever
✅ **Docs**: Great documentation
⚠️ **Paid**: No longer has free tier

**Steps:**
1. Go to [heroku.com](https://heroku.com)
2. Create account and install Heroku CLI
3. Run in your terminal:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

## 🛠️ Pre-Deployment Checklist

Before deploying, make sure:
- ✅ All tests pass: `python quick_test.py`
- ✅ Requirements are up to date: `pip freeze > requirements.txt`
- ✅ Environment variables are set correctly
- ✅ Debug mode is disabled in production

## 🔧 Environment Variables

For production deployment, set these variables:
- `FLASK_ENV=production`
- `PORT=5000` (or whatever your platform uses)

## 📊 Deployment Files Included

Your project includes deployment configurations for:
- **`railway.toml`** - Railway deployment
- **`render.yaml`** - Render deployment
- **`vercel.json`** - Vercel deployment
- **`Procfile`** - Heroku deployment

## 🎉 After Deployment

Once deployed, your calculator will have:
- **Sample Size Calculator** at `/sample-size-calculator`
- **Sequential Testing** at `/sequential-calculator`
- **Standard Deviation Calculator** at `/std-calculator`
- **Home Page** at `/`

## 🔄 Updating Your Live Calculator

To update your live calculator:
1. Make changes locally
2. Test: `python quick_test.py`
3. Commit: `git add . && git commit -m "Update message"`
4. Push: `git push origin main`
5. Your deployment platform will automatically redeploy!

## 🆘 Troubleshooting

### Common Issues:
- **Build fails**: Check `requirements.txt` has all needed packages
- **App won't start**: Verify `app.py` has correct Flask configuration
- **404 errors**: Make sure routes are defined correctly

### Getting Help:
- Check deployment platform logs
- Verify environment variables are set
- Test locally first: `python run_app.py`

## 💡 Pro Tips

1. **Use Railway** - It's the easiest and most reliable
2. **Check logs** - All platforms provide deployment logs
3. **Test locally** - Always test with `python quick_test.py` before deploying
4. **Monitor usage** - Check your platform's dashboard for usage stats

---

🎯 **Ready to deploy?** Start with Railway - it's configured and ready to go!

Your calculator will be available 24/7 online for anyone to use! 🌐
