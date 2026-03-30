# MongoDB Quick Start - 5 Minute Setup

## 🎯 What You Need to Do

1. **Get MongoDB Connection URL** (5 minutes)
2. **Add it to your .env file** (30 seconds)
3. **Test the connection** (30 seconds)
4. **Run your app** (Done!)

---

## 📝 Step-by-Step Instructions

### Step 1: Get Your MongoDB URL

1. Go to: **https://www.mongodb.com/cloud/atlas/register**
2. Sign up (use Google for fastest signup)
3. Create a FREE cluster (M0 Sandbox)
4. Create a database user:
   - Username: `quantpulse_user`
   - Password: Click "Autogenerate" and **SAVE IT**
5. Whitelist IP: Click "Allow Access from Anywhere"
6. Get connection string:
   - Click "Connect" → "Connect your application"
   - Copy the connection string
   - Replace `<username>` with your username
   - Replace `<password>` with your password
   - Add `/quantpulse` before the `?`

**Example connection string:**
```
mongodb+srv://quantpulse_user:YourPassword123@cluster0.xxxxx.mongodb.net/quantpulse?retryWrites=true&w=majority
```

### Step 2: Add to .env File

1. Open `QuantPulse-Backend/.env` file
2. Find the line: `MONGODB_URL="mongodb://localhost:27017/quantpulse"`
3. Replace it with your connection string from Step 1
4. Save the file

**Example:**
```env
MONGODB_URL="mongodb+srv://quantpulse_user:YourPassword123@cluster0.xxxxx.mongodb.net/quantpulse?retryWrites=true&w=majority"
```

### Step 3: Install Packages

Open terminal in `QuantPulse-Backend` folder and run:

```bash
pip install pymongo motor
```

### Step 4: Test Connection

Run the test script:

```bash
python test_mongodb.py
```

**Expected output:**
```
✅ Found MONGODB_URL in .env file
✅ Successfully connected to MongoDB!
✅ Health check passed
🎉 SUCCESS! MongoDB is working perfectly!
```

### Step 5: Run Your Application

```bash
python run.py
```

Your app will now use MongoDB! 🎉

---

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "Authentication failed" | Check username/password in connection string |
| "Connection timeout" | Whitelist your IP in MongoDB Atlas |
| "MONGODB_URL not found" | Make sure you edited `.env` (not `.env.example`) |
| "No module named pymongo" | Run: `pip install pymongo motor` |

---

## 📚 Need More Details?

See the full guide: **MONGODB_SETUP_GUIDE.md**

---

## ✅ What's Working Now?

- ✅ MongoDB connection code is ready
- ✅ Integrated into your FastAPI app
- ✅ Test script created
- ✅ Automatic connection on app startup
- ✅ Automatic cleanup on app shutdown

**All you need to do is add your MongoDB URL to the .env file!**
