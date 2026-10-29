# 🎣 Would I Fall For It? - Phishing Awareness Trainer

A small Flask web app that trains people to spot phishing. Instead of scanning links, it shows realistic emails, SMS and WhatsApp messages and asks: **phishing or legit?** After each answer it explains the clues you should have noticed.

![screenshot](screenshot.png)

## Features
- 22 realistic scenarios: look-alike domains, subdomain tricks, fake urgency, hidden links, QR code scams, dangerous attachments, OTP scams, CEO fraud, changed payment details, hacked friend accounts, fee scams, and real messages that look suspicious
- 3 difficulty levels (Easy, Medium, Hard) with random 8-question rounds
- "Check where the link really goes" button to reveal hidden link destinations
- Answers are checked on the server, so the correct answer is not visible in the page
- End-of-round score, a breakdown of which scam types you miss most, and your best score per level
- Learn page with 8 habits to spot phishing and what to do if you already clicked

## Run it
```
pip install -r requirements.txt
python app.py
```
Then open http://127.0.0.1:5000

## Tech
Python, Flask, vanilla JavaScript, HTML/CSS

## Ideas for next versions
- Load scenarios from a JSON file so others can contribute
- Add a timer mode
- Save scores in a database