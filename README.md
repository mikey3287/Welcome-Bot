# Created By Mikey

# 🤖 Welcome Bot — Discord.py

A customizable Discord Welcome Bot built with **Python & discord.py**.  
Automatically welcomes new members, sends goodbye messages, warns about suspicious accounts, and supports full configuration using a `config.json` file and slash commands.

---

## ✨ Features

### ⭐ Welcome Message
- Clean embed design
- Shows profile name, username, global name
- Displays account creation date
- Calculates account age (days)
- Member number on join
- Avatar included

### ⭐ Goodbye Message
- Clean farewell embed
- Shows full user profile

### ⭐ Suspicious Account Detection
- Warns if account age is below your configured limit
- Sends alerts to a mod-log channel
- Optional auto-role for new users

### ⭐ Config System (`config.json`)
You can update bot settings **without editing code**:

- Welcome channel  
- Goodbye channel  
- Mod-log channel  
- Minimum account age  
- Auto-role for new users  
- Admin roles  
- Themes (optional)

### ⭐ Admin Slash Commands
#### `/setconfig key:... value:...`
Update any config value instantly.

#### `/test_welcome`
Preview what the welcome message looks like.

### ⭐ Modern Codebase
- Supports Python 3.10+  
- Uses virtual environments  
- Easy to host anywhere (local, VPS, Docker, Replit, etc.)

---

## 🛠 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/mikey3287/Welcome-Bot.git
cd Welcome-Bot
