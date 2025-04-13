# Cumarmor  
**Developed by** - yellow (@yellowfire_fighter)  
Join the Discord: [https://discord.gg/gjpq4K9GuY](https://discord.gg/gjpq4K9GuY)  

---

## Overview  
**Cumarmor** is a Luau whitelist authentication system built for Roblox experiences. It features a Tornado-based backend, a MySQL database, and a Discord bot using Discord.py. This system allows secure key generation and verification for users accessing your game.  

> ⚠️ **Note:** This repository does **not** include encoding or anti-tamper logic to protect the whitelist client or keys. This is intentional—you should implement your own custom protection mechanisms to secure your deployment.  

---

## Features  
- 🔐 Discord-based whitelist key generation and validation  
- 🧠 MySQL integration for persistent data storage  
- 🌐 Tornado web server backend for real-time handling  
- ⚙️ Easy integration with Roblox scripts using HTTP requests  
- 🚫 Licensed for **non-commercial** use only  

---

## Installation  

### Requirements  
- Python 3.9+  
- MySQL server  
- Pip packages:  
```bash
pip install discord.py mysql-connector-python tornado requests
```  

### Setup  

1. **Clone the Repository**  
```bash
git clone https://github.com/yourusername/Cumarmor.git  
cd Cumarmor
```  

2. **Configure MySQL**  
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

3. **Start the Services**  
Run the Discord bot and the Tornado server. You can do this in separate threads or terminal instances. The bot handles key generation, and the server validates them.

---

## Usage  
- Admins can generate keys through Discord using commands (not included here for security).  
- Users submit their key through a Roblox GUI, which sends an HTTP request to the Tornado backend.  
- The backend validates the key against the MySQL database.  

---

## License  
This project is licensed under the **Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0)**.  
You may use, share, and adapt the code for **non-commercial purposes only**, and **must provide appropriate credit**.  
[Read the full license here.](https://creativecommons.org/licenses/by-nc/4.0/)  

---

## Contributing  
Contributions are welcome! Feel free to submit issues or open a pull request. Please stick to non-commercial use and respect the license terms.  

---

## Disclaimer  
This repository does **not** include:  
- Obfuscation/Encoding  
- Anti-tamper measures  
- Full command list or key generation logic  

These are left out intentionally to keep the system clean and for you to implement your own protections and enhancements. You are responsible for securing your own deployment.  

---

## Contact  
Need help or want to share how you use Cumarmor?  
Join the community: [https://discord.gg/gjpq4K9GuY](https://discord.gg/gjpq4K9GuY)
