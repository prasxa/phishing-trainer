# 🎣 Would I Fall For It? - Phishing Awareness Trainer

A small Flask web app that trains people to spot phishing. Instead of scanning links, it shows realistic emails, SMS and WhatsApp messages and asks: **phishing or legit?** After each answer it explains the clues you should have noticed.

![screenshot](screenshot.png)

## Features
- 12 realistic scenarios (look-alike domains, fake urgency, hidden links, dangerous attachments, OTP scams, CEO fraud, fee scams) plus real-looking safe messages
- Random 8-question rounds (5 phishing, 3 legit) so it never feels the same
- "Check where the link really goes" button to reveal hidden link destinations
- Answers are checked on the server, so the correct answer is not visible in the page
- End-of-round score and a breakdown of which scam types you miss most

## Run it
```
pip install -r requirements.txt
python app.py
```
Then open http://127.0.0.1:5000

## Tech
Python, Flask, vanilla JavaScript, HTML/CSS

## Ideas for next versions
- Add more scenarios and difficulty levels
- Save scores over time
- Load scenarios from a JSON file so others can contribute