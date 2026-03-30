# MongoDB Setup Guide

This guide will walk you through setting up MongoDB for your QuantPulse project, step by step.

## What is MongoDB?

MongoDB is a database where we'll store user data, stock information, and predictions. Think of it as a digital filing cabinet for your application.

---

## Step 1: Create a Free MongoDB Account

1. **Go to MongoDB Atlas website:**
   - Open your browser and go to: https://www.mongodb.com/cloud/atlas/register
   
2. **Sign up for a free account:**
   - Click "Try Free" or "Sign Up"
   - You can sign up with:
     - Google account (easiest)
     - Email and password
   
3. **Choose the FREE tier:**
   - Select "M0 Sandbox" (FREE forever)
   - Choose a cloud provider (AWS, Google Cloud, or Azure - doesn't matter)
   - Choose a region close to you (for better speed)
   - Click "Create Cluster"

---

## Step 2: Create Your Database

1. **Wait for cluster creation:**
   - This takes 1-3 minutes
   - You'll see a progress bar
   
2. **Create a database user:**
   - Click "Database Access" in the left sidebar
   - Click "Add New Database User"
   - Choose "Password" authentication
   - Enter a username (example: `quantpulse_user`)
   - Click "Autogenerate Secure Password" or create your own
   - **IMPORTANT:** Copy and save this password somewhere safe!
   - Set privileges to "Read and write to any database"
   - Click "Add User"

3. **Whitelist your IP address:**
   - Click "Network Access" in the left sidebar
   - Click "Add IP Address"
   - Click "Allow Access from Anywhere" (for development)
   - Click "Confirm"
   - **Note:** For production, you should whitelist only specific IPs

---

## Step 3: Get Your Connection String

1. **Go to your cluster:**
   - Click "Database" in the left sidebar
   - You should see your cluster (named something like "Cluster0")
   
2. **Click "Connect":**
   - Click the "Connect" button on your cluster
   
3. **Choose connection method:**
   - Click "Connect your application"
   
4. **Copy the connection string:**
   - You'll see a string that looks like this:
     ```
     mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
     ```
   
5. **Modify the connection string:**
   - Replace `<username>` with your database username
   - Replace `<password>` with your database password
   - Add your database name at the end (before the `?`)
   
   **Example:**
   ```
   Original:
   mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   
   Modified:
   mongodb+srv://quantpulse_user:MySecurePass123@cluster0.xxxxx.mongodb.net/quantpulse?retryWrites=true&w=majority
   ```
   
   Notice:
   - `<username>` → `quantpulse_user`
   - `<password>` → `MySecurePass123`
   - Added `/quantpulse` before the `?`

---

## Step 4: Add Connection String to Your Project

1. **Open your project folder:**
   - Navigate to `QuantPulse-Backend` folder
   
2. **Open the `.env` file:**
   - Find the file named `.env` (not `.env.example`)
   - Open it with any text editor (Notepad, VS Code, etc.)
   
3. **Find the MONGODB_URL line:**
   - Look for this line:
     ```
     MONGODB_URL="mongodb://localhost:27017/quantpulse"
     ```
   
4. **Replace it with your connection string:**
   - Replace the entire value with your MongoDB Atlas connection string
   - Keep the quotes around it
   
   **Example:**
   ```
   MONGODB_URL="mongodb+srv://quantpulse_user:MySecurePass123@cluster0.xxxxx.mongodb.net/quantpulse?retryWrites=true&w=majority"
   ```
   
5. **Save the file**

---

## Step 5: Install Required Packages

1. **Open terminal/command prompt:**
   - Navigate to your `QuantPulse-Backend` folder
   
2. **Run this command:**
   ```bash
   pip install pymongo motor
   ```
   
   This installs the MongoDB drivers for Python.

---

## Step 6: Test Your Connection

1. **In the terminal, run:**
   ```bash
   python test_mongodb.py
   ```
   
2. **What you should see:**
   - ✅ Found MONGODB_URL in .env file
   - ✅ Successfully connected to MongoDB!
   - ✅ Health check passed
   - ✅ Test operations completed
   - 🎉 SUCCESS! MongoDB is working perfectly!

3. **If you see errors:**
   - Check if your username/password is correct
   - Check if you whitelisted your IP address
   - Check if your internet connection is working
   - Make sure you added `/quantpulse` to the connection string

---

## Step 7: Run Your Application

Once the test passes, you can run your application:

```bash
python run.py
```

Your application will now connect to MongoDB automatically!

---

## Troubleshooting

### Error: "Authentication failed"
- Double-check your username and password in the connection string
- Make sure there are no special characters that need URL encoding
- If your password has special characters like `@`, `#`, `%`, you need to URL encode them

### Error: "Connection timeout"
- Check if you whitelisted your IP address in MongoDB Atlas
- Check your internet connection
- Try "Allow Access from Anywhere" in Network Access settings

### Error: "MONGODB_URL not found"
- Make sure you edited the `.env` file (not `.env.example`)
- Make sure the file is saved
- Restart your terminal/command prompt

### Error: "No module named 'pymongo'"
- Run: `pip install pymongo motor`
- Make sure you're in the correct Python environment

---

## Security Notes

1. **Never commit your `.env` file to Git**
   - It contains sensitive passwords
   - The `.gitignore` file should already exclude it

2. **For production:**
   - Use strong passwords
   - Whitelist only specific IP addresses
   - Use environment variables on your hosting platform

3. **Keep your connection string secret:**
   - Don't share it publicly
   - Don't post it in forums or chat
   - Treat it like a password

---

## What's Next?

Now that MongoDB is connected, you can:
- Store user accounts in the database
- Save stock predictions
- Cache market data
- Store user preferences and settings

The application will automatically use MongoDB for all database operations!

---

## Need More Help?

- MongoDB Atlas Documentation: https://docs.atlas.mongodb.com/
- MongoDB University (Free Courses): https://university.mongodb.com/
- Contact MongoDB Support: https://support.mongodb.com/

---

**Congratulations! You've successfully set up MongoDB for your QuantPulse project! 🎉**
