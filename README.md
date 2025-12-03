# Cumarmor  
**Developed by** - yellow (@yellowfire_fighter)  
Join the Discord: [https://discord.gg/J9G9GjTYTX](https://discord.gg/J9G9GjTYTX)

---

## Overview  
**Cumarmor** is a Luau whitelist authentication system built for Roblox experiences. It features a Tornado-based backend, a MySQL database, and a Discord bot using Discord.py. This system allows secure key generation and verification for users accessing your script.  

>  **Note:** This code is about 3 years old and has not been updated much, this would be good to use as a base for your own whitelist.  

---

## Features  
-  Discord-based whitelist key generation and validation  
-  MySQL integration for persistent data storage  
-  Tornado web server backend for real-time handling  
-  Easy integration with Roblox scripts using HTTP requests

---

## Installation  

### Requirements  
- Python 3.9+  
- MySQL server  
- Pip packages

### Setup  

1. **Clone the Repository**  
```bash
git clone https://github.com/yourusername/Cumarmor.git  
cd Cumarmor
```

2. **Install Packages**
Run the install.bat file

3. **Configure MySQL**  
Make sure your MySQL server is running and accessible. Edit your database credentials in the Python files:  
```python
conn = mysql.connector.connect(
  host="localhost",
  user="root",
  password="root",
  auth_plugin='mysql_native_password',
  pool_name = "sqlpool",
  pool_size = 3
)
```  

4. **Start the Services**  
Run the Discord bot and the Tornado server. You can do this in separate threads or terminal instances.

---

## Usage  
- Admins can generate keys through Discord using commands (not included here for security).  
- Users submit their key through the script, which sends an HTTP request to the Tornado backend.  
- The backend validates the key against the MySQL database.  

---

## Info
- Any expired keys will be deleted and the users role will be removed
- This was made for my use only so it is not very customizable
- Some parts of it have been removed as they are important to security

---

## Contributing  
Contributions are welcome! Feel free to submit issues or open a pull request. Please stick to non-commercial use and respect the license terms.  
Anyone who contributes will be credited

---
