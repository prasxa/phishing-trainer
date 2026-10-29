from flask import Flask, jsonify, request, Response
import random

app = Flask(__name__)

SCENARIOS = [
    {
        "id": 1, "difficulty": "easy", "channel": "Email",
        "sender": "security@paypa1-support.com",
        "subject": "Your account is limited - action required",
        "body": "Dear Customer,\n\nWe noticed unusual activity. Your account will be closed in 24 hours unless you confirm your details.\n\nThank you,\nSecurity Team",
        "link_shown": "Confirm my account",
        "link_real": "http://paypa1-support.com/verify",
        "is_phish": True, "category": "Look-alike domain",
        "clues": [
            "The sender domain uses the number 1 instead of the letter l (paypa1)",
            "Threatens to close your account in 24 hours (fake urgency)",
            "Starts with 'Dear Customer' instead of your real name",
        ],
        "explanation": "Attackers register domains that look almost identical to real brands and rely on you reading quickly.",
    },
    {
        "id": 2, "difficulty": "medium", "channel": "Email",
        "sender": "no-reply@accounts.google.com",
        "subject": "Security alert: new sign-in on Windows",
        "body": "Your Google Account was just signed in to from a new Windows device.\n\nIf this was you, you don't need to do anything. If not, please review your recent activity.",
        "link_shown": "Check activity",
        "link_real": "https://myaccount.google.com/notifications",
        "is_phish": False, "category": "None",
        "clues": [
            "The sender domain is the real accounts.google.com",
            "The link goes to a real google.com address over HTTPS",
            "It informs you; it does not threaten you or demand anything",
        ],
        "explanation": "This looks legitimate. Even so, the safest habit is to open the site yourself instead of clicking the link.",
    },
    {
        "id": 3, "difficulty": "easy", "channel": "SMS",
        "sender": "+91 90000 12345",
        "subject": "",
        "body": "Your parcel is held at the depot due to an incomplete address. Pay Rs 25 redelivery fee within 2 hours or it will be returned.",
        "link_shown": "http://bit.ly/3xParcel",
        "link_real": "Hidden behind a link shortener - you cannot see the real destination",
        "is_phish": True, "category": "Small fee trick",
        "clues": [
            "A tiny fee makes people relax and enter card details",
            "A 2-hour deadline creates panic",
            "Shortened links hide where you are really going",
        ],
        "explanation": "The goal is your card details, not the Rs 25. Always track parcels in the courier's official app.",
    },
    {
        "id": 4, "difficulty": "medium", "channel": "Email",
        "sender": "hr-team@company-benefits.co",
        "subject": "Updated leave policy - please sign today",
        "body": "Hi,\n\nPlease review and e-sign the updated leave policy before 5 PM today. Everyone must complete this.\n\nHR Team",
        "link_shown": "https://intranet.yourcompany.com/leave-policy",
        "link_real": "http://yourcompany-intranet.co/login",
        "is_phish": True, "category": "Hidden link mismatch",
        "clues": [
            "The text of the link says one thing, but it really goes somewhere else",
            "The real link is not HTTPS and uses a different domain (.co)",
            "The sender is not your company's real email domain",
        ],
        "explanation": "Always check where a link really goes. What is shown on screen can be anything.",
    },
    {
        "id": 5, "difficulty": "easy", "channel": "Email",
        "sender": "library@university.edu",
        "subject": "Reminder: book due tomorrow",
        "body": "Hello,\n\nThe book 'Computer Networks' is due tomorrow. You can renew it from your library account.\n\nCentral Library",
        "link_shown": "Renew my book",
        "link_real": "https://library.university.edu/account",
        "is_phish": False, "category": "None",
        "clues": [
            "The sender domain matches the institution",
            "The link uses HTTPS and stays on the same domain",
            "It has specific details (the book title) and no threats",
        ],
        "explanation": "Looks legitimate, assuming you really borrowed that book.",
    },
    {
        "id": 6, "difficulty": "easy", "channel": "Email",
        "sender": "billing@acc0unts-dept.net",
        "subject": "Invoice 8841 - payment overdue",
        "body": "Hello,\n\nPlease find the overdue invoice attached. Open it today to avoid late fees.\n\nAttachment: Invoice_8841.pdf.exe",
        "link_shown": "",
        "link_real": "",
        "is_phish": True, "category": "Dangerous attachment",
        "clues": [
            "'.pdf.exe' means it is a program, not a document",
            "The sender domain uses a zero instead of the letter o (acc0unts)",
            "Late fees are used to rush you into opening it",
        ],
        "explanation": "A hidden double file extension is a classic way to get you to run malware.",
    },
    {
        "id": 7, "difficulty": "easy", "channel": "WhatsApp",
        "sender": "+44 7000 123456",
        "subject": "",
        "body": "Hi! We found your resume. Work from home and earn Rs 5000 per day just by liking videos. Pay a refundable registration fee of Rs 2000 to start today. Limited seats!",
        "link_shown": "",
        "link_real": "",
        "is_phish": True, "category": "Too good to be true",
        "clues": [
            "You did not apply, yet they contacted you first",
            "Very high pay for very easy work",
            "A real job never asks you to pay money first",
            "'Limited seats' adds pressure",
        ],
        "explanation": "This is a fee scam. The money you send is the whole point.",
    },
    {
        "id": 8, "difficulty": "medium", "channel": "SMS",
        "sender": "VM-MYBANK",
        "subject": "",
        "body": "123456 is your OTP for a payment of Rs 1,200 at ExampleStore. Do not share this OTP with anyone. Bank staff never ask for it.",
        "link_shown": "",
        "link_real": "",
        "is_phish": False, "category": "None",
        "clues": [
            "No link and no request to reply or call",
            "It warns you not to share the OTP",
            "It only makes sense if you just started that payment",
        ],
        "explanation": "Legitimate if you made the payment. If you did not, call your bank using the number on your card.",
    },
    {
        "id": 9, "difficulty": "easy", "channel": "SMS",
        "sender": "AX-BANKKYC",
        "subject": "",
        "body": "Dear user, your KYC has expired and your account will be blocked today. Share the OTP sent to your phone to update KYC, or call 98000 00000 now.",
        "link_shown": "",
        "link_real": "",
        "is_phish": True, "category": "Asks for secrets",
        "clues": [
            "No bank ever asks you to share an OTP",
            "'Blocked today' is fake urgency",
            "It asks you to call a personal mobile number",
            "Generic greeting: 'Dear user'",
        ],
        "explanation": "An OTP is a key to your money. Sharing it lets the attacker approve payments as you.",
    },
    {
        "id": 10, "difficulty": "medium", "channel": "Email",
        "sender": "Rahul Sharma (CEO) <rahul.ceo.office@gmail.com>",
        "subject": "Quick favour - confidential",
        "body": "Hi, I'm in a meeting and can't talk. I need 5 gift cards of Rs 5000 for clients right now. Buy them and send me the codes here. I'll pay you back today. Keep this between us.",
        "link_shown": "",
        "link_real": "",
        "is_phish": True, "category": "Fake authority",
        "clues": [
            "A CEO writing from a free Gmail address",
            "Gift card codes are a favorite payment method for scammers",
            "'Keep this between us' stops you from checking with anyone",
            "Says they can't talk, so you can't verify by phone",
        ],
        "explanation": "This is called CEO fraud. Pretending to be a boss makes people skip their normal checks.",
    },
    {
        "id": 11, "difficulty": "easy", "channel": "Email",
        "sender": "shipment-tracking@amazon.in",
        "subject": "Your package is out for delivery",
        "body": "Hello,\n\nYour package will arrive today. You can see the status in your orders.\n\nThank you for shopping with us.",
        "link_shown": "Track package",
        "link_real": "https://www.amazon.in/your-orders",
        "is_phish": False, "category": "None",
        "clues": [
            "The sender domain is the real amazon.in",
            "The link goes to the same real domain over HTTPS",
            "No payment, password, or OTP is requested",
        ],
        "explanation": "Looks legitimate, assuming you actually ordered something.",
    },
    {
        "id": 12, "difficulty": "easy", "channel": "Email",
        "sender": "no-reply@coursera.org",
        "subject": "Your weekly learning summary",
        "body": "You completed 3 lessons this week. Keep going!",
        "link_shown": "Continue learning",
        "link_real": "https://www.coursera.org/learn",
        "is_phish": False, "category": "None",
        "clues": [
            "The sender domain matches the real site",
            "The link matches the sender and uses HTTPS",
            "Nothing is demanded and nothing is urgent",
        ],
        "explanation": "A normal newsletter-style message with no red flags.",
    },
    {
        "id": 13, "difficulty": "hard", "channel": "Email",
        "sender": "it-support@yourcompany.com",
        "subject": "Password expires in 24 hours",
        "body": "Hello,\n\nYour network password will expire soon. To keep your access, please update it using the secure portal below.\n\nIT Support",
        "link_shown": "https://yourcompany.com/password-update",
        "link_real": "https://yourcompany.com.secure-login.net/update",
        "is_phish": True, "category": "Subdomain trick",
        "clues": [
            "The real website is the end of the address, before the first '/': secure-login.net",
            "Attackers put your company's name at the start of a longer address to fool you",
            "The link you see and the link you really get are different",
            "A password-expiry deadline is a favorite phishing story",
        ],
        "explanation": "Read a web address up to the first '/'. The last two parts before it show who really owns the site.",
    },
    {
        "id": 14, "difficulty": "hard", "channel": "Email",
        "sender": "noreply@github.com",
        "subject": "Reset your password",
        "body": "We received a request to reset the password for your account. Use the button below to choose a new one.\n\nIf you didn't ask for this, you can ignore this email.",
        "link_shown": "Reset password",
        "link_real": "https://github.com/password_reset",
        "is_phish": False, "category": "None",
        "clues": [
            "The sender domain is the real github.com",
            "The link goes to github.com over HTTPS",
            "No threat or deadline, and it says you can ignore it",
        ],
        "explanation": "Legit only if you actually asked for a reset. If you did not, do not click. Just ignore it, or go to the site yourself and change your password.",
    },
    {
        "id": 15, "difficulty": "medium", "channel": "SMS",
        "sender": "+91 88000 55555",
        "subject": "",
        "body": "Traffic e-challan of Rs 500 is pending on your vehicle. Scan the QR code in the image to pay before the fine doubles.",
        "link_shown": "[QR code image attached]",
        "link_real": "http://echallan-pay.top/pay (this is what the QR code opens)",
        "is_phish": True, "category": "QR code trick",
        "clues": [
            "A QR code hides the real address from you",
            "'Before the fine doubles' is a pressure tactic",
            "Message from an unknown number, not an official source",
            "Real fines are paid on the official government site that you type yourself",
        ],
        "explanation": "Scam QR codes are called quishing. Never pay or log in through a QR code that arrives in a message.",
    },
    {
        "id": 16, "difficulty": "hard", "channel": "Email",
        "sender": "accounts@globex-supplies.co",
        "subject": "Re: Invoice 5521 - new bank details",
        "body": "Hello,\n\nPlease note our bank account has changed. Send the payment for invoice 5521 to the new account below before Friday.\n\nNew account: 0000 1111 2222\n\nThanks,\nAccounts Team",
        "link_shown": "",
        "link_real": "",
        "is_phish": True, "category": "Changed payment details",
        "clues": [
            "The sender ends in .co, but past emails from this supplier came from .com",
            "Changes to bank details are a classic fraud and must be confirmed by phone on a known number",
            "A payment deadline adds pressure",
            "'Re:' in the subject makes it feel like an old, trusted conversation",
        ],
        "explanation": "This is business email compromise. Never change payment details based on an email alone.",
    },
    {
        "id": 17, "difficulty": "medium", "channel": "Email",
        "sender": "alerts@yourbank.com",
        "subject": "Your October statement is ready",
        "body": "Hello,\n\nYour account statement for October is ready. Please open your banking app or website to view it.\n\nWe will never ask for your password, PIN or OTP by email.",
        "link_shown": "",
        "link_real": "",
        "is_phish": False, "category": "None",
        "clues": [
            "No link and no attachment to click",
            "It tells you to open the app or website yourself",
            "No urgency or threats, and a clear safety reminder",
        ],
        "explanation": "A safe style of message. The best habit is exactly what it says: open the banking app yourself.",
    },
    {
        "id": 18, "difficulty": "hard", "channel": "Email",
        "sender": "priya.k@college.edu",
        "subject": "Notes you asked for",
        "body": "Hey! Here are the notes you asked for. Let me know if they open fine :)",
        "link_shown": "notes_final.pdf",
        "link_real": "https://docs-share-viewer.com/open?id=83hd",
        "is_phish": True, "category": "Hacked friend account",
        "clues": [
            "You never asked for any notes",
            "The message is vague, with no subject name or details",
            "The link goes to an unknown site, not your college or a known file service",
            "A real sender address can still be a hacked account, so check by another channel",
        ],
        "explanation": "Attackers often use a hacked account of someone you know. Judge the request and the link, not just the sender name.",
    },
    {
        "id": 19, "difficulty": "easy", "channel": "WhatsApp",
        "sender": "+91 70000 99999",
        "subject": "",
        "body": "CONGRATULATIONS! Your mobile number won Rs 25,00,000 in the Lucky Draw. To claim your prize, send Rs 5000 processing fee to our agent today.",
        "link_shown": "",
        "link_real": "",
        "is_phish": True, "category": "Prize scam",
        "clues": [
            "You never entered any draw",
            "You must pay money to receive money",
            "'Today' adds urgency",
            "It comes from a random unknown number",
        ],
        "explanation": "Real prizes never ask you to pay a fee first.",
    },
    {
        "id": 20, "difficulty": "medium", "channel": "Email",
        "sender": "alert@microsoft-support-help.com",
        "subject": "WARNING: Virus detected on your computer",
        "body": "Your computer is infected and your data is at risk! Call our certified technician now at 1800-000-0000 to remove it. Do not turn off your computer.",
        "link_shown": "",
        "link_real": "",
        "is_phish": True, "category": "Fake tech support",
        "clues": [
            "Big companies do not email virus alerts with a phone number to call",
            "The domain is not the company's real domain",
            "Scary words and 'do not turn off' create panic",
            "Calling usually leads to someone asking for remote access to your computer",
        ],
        "explanation": "Fake tech support scams want you to call so they can take control of your device or charge you.",
    },
    {
        "id": 21, "difficulty": "hard", "channel": "Email",
        "sender": "messages-noreply@linkedin.com",
        "subject": "You have a new message",
        "body": "A recruiter sent you a message. Open LinkedIn to read and reply.",
        "link_shown": "View message",
        "link_real": "https://www.linkedin.com/messaging",
        "is_phish": False, "category": "None",
        "clues": [
            "The sender domain is the real linkedin.com",
            "The link goes to linkedin.com over HTTPS",
            "No personal details or payment are requested",
        ],
        "explanation": "Looks legitimate. Not every email with a link is a trap. Safest habit: open the app yourself.",
    },
    {
        "id": 22, "difficulty": "hard", "channel": "Email",
        "sender": "mailbox-admin@rnicrosoft-online.com",
        "subject": "Your mailbox is 98% full",
        "body": "Hello,\n\nYour mailbox storage is almost full. Incoming mail will stop in 12 hours. Click below to increase your storage for free.\n\nMailbox Admin Team",
        "link_shown": "Increase storage",
        "link_real": "http://rnicrosoft-online.com/storage",
        "is_phish": True, "category": "Look-alike letters (rn vs m)",
        "clues": [
            "'rn' next to each other looks like 'm' at a quick glance (rnicrosoft)",
            "A 12-hour deadline creates pressure",
            "The link is not HTTPS",
            "Generic sign-off: 'Mailbox Admin Team'",
        ],
        "explanation": "Read the sender's address slowly, letter by letter. Look-alike letters are easy to miss.",
    },
]

LEVELS = {
    "easy": ["easy"],
    "medium": ["easy", "medium"],
    "hard": ["medium", "hard"],
}

STYLE = """
  body{font-family:Segoe UI,Arial,sans-serif;background:#0f172a;color:#e2e8f0;margin:0;padding:24px;}
  .wrap{max-width:680px;margin:0 auto;}
  h1{margin:0 0 4px;}
  .sub{color:#94a3b8;margin-bottom:20px;}
  .nav{margin-bottom:16px;}
  .nav a{color:#93c5fd;margin-right:16px;text-decoration:none;font-weight:600;}
  .card{background:#1e293b;border-radius:12px;padding:20px;margin-bottom:16px;}
  .meta{color:#94a3b8;font-size:14px;margin:2px 0;}
  .body{white-space:pre-wrap;margin:14px 0;line-height:1.5;}
  button{font-size:16px;padding:10px 18px;border:0;border-radius:8px;cursor:pointer;margin-right:8px;margin-bottom:8px;color:#fff;}
  .phish{background:#dc2626;}
  .legit{background:#16a34a;}
  .neutral{background:#3b82f6;}
  .peek{background:#475569;font-size:14px;padding:6px 12px;margin-top:8px;}
  .link{font-family:Consolas,monospace;font-size:14px;margin-top:8px;}
  .real{color:#fbbf24;}
  .good{color:#4ade80;}
  .bad{color:#f87171;}
  .hidden{display:none;}
  ul,ol{padding-left:20px;line-height:1.6;}
  li{margin-bottom:8px;}
"""

NAV = '<div class="nav"><a href="/">🎮 Play</a><a href="/learn">📘 Learn</a></div>'

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Would I Fall For It?</title>
<style>__STYLE__</style>
</head>
<body>
<div class="wrap">
  __NAV__
  <h1>🎣 Would I Fall For It?</h1>
  <div class="sub">Read the message. Is it phishing or legit?</div>

  <div id="start" class="card">
    <p>You will see 8 messages. Decide if each one is a phishing attempt or a real message. Pick a level:</p>
    <div>
      <button class="neutral lvl" data-level="easy">🟢 Easy</button>
      <button class="neutral lvl" data-level="medium">🟡 Medium</button>
      <button class="neutral lvl" data-level="hard">🔴 Hard</button>
    </div>
    <div class="meta">Easy = obvious scams. Medium = a mix. Hard = tricky scams, and real messages that look suspicious.</div>
    <div class="meta" id="bests" style="margin-top:10px;"></div>
  </div>

  <div id="quiz" class="hidden">
    <div class="meta" id="progress"></div>
    <div class="card">
      <div class="meta" id="channel"></div>
      <div class="meta" id="sender"></div>
      <div class="meta" id="subject"></div>
      <div class="body" id="body"></div>
      <div class="link" id="linkShown"></div>
      <div class="link real hidden" id="linkReal"></div>
      <button class="peek" id="peekBtn">👁 Check where the link really goes</button>
    </div>
    <div id="choices">
      <button class="phish" id="btnPhish">🚩 Phishing</button>
      <button class="legit" id="btnLegit">✅ Legit</button>
    </div>
    <div id="feedback" class="card hidden">
      <h3 id="fbTitle"></h3>
      <div id="fbExplain"></div>
      <div class="meta" id="fbClueTitle" style="margin-top:12px;"></div>
      <ul id="fbClues"></ul>
      <button class="neutral" id="nextBtn">Next</button>
    </div>
  </div>

  <div id="end" class="card hidden">
    <h2 id="endScore"></h2>
    <div id="endRating"></div>
    <div class="meta" id="endBest" style="margin-top:8px;"></div>
    <div class="meta" style="margin-top:12px;">Where you slipped:</div>
    <ul id="endMissed"></ul>
    <button class="neutral" id="againBtn">Play again</button>
    <a href="/learn" style="color:#93c5fd;">📘 Read the phishing tips</a>
  </div>
</div>

<script>
let questions = [];
let idx = 0;
let score = 0;
let missed = {};
let answered = false;
let level = "easy";

function $(id){ return document.getElementById(id); }

function cap(s){ return s.charAt(0).toUpperCase() + s.slice(1); }

function loadBest(l){
  try {
    const v = localStorage.getItem("best_" + l);
    return v === null ? null : parseInt(v, 10);
  } catch (e) { return null; }
}

function saveBest(l, s){
  try {
    const old = loadBest(l);
    if (old === null || s > old){ localStorage.setItem("best_" + l, String(s)); }
  } catch (e) {}
}

function showBests(){
  const parts = ["easy", "medium", "hard"].map(function(l){
    const b = loadBest(l);
    return cap(l) + ": " + (b === null ? "-" : b + "/8");
  });
  $("bests").textContent = "Your best scores → " + parts.join("   |   ");
}

async function startRound(l){
  level = l;
  const res = await fetch("/api/round?level=" + l);
  questions = await res.json();
  idx = 0; score = 0; missed = {};
  $("start").classList.add("hidden");
  $("end").classList.add("hidden");
  $("quiz").classList.remove("hidden");
  showQuestion();
}

function showQuestion(){
  const q = questions[idx];
  answered = false;
  $("progress").textContent = "Level: " + cap(level) + "   |   Question " + (idx + 1) + " of " + questions.length + "   |   Score: " + score;
  $("channel").textContent = "Channel: " + q.channel;
  $("sender").textContent = "From: " + q.sender;
  $("subject").textContent = q.subject ? "Subject: " + q.subject : "";
  $("body").textContent = q.body;

  if (q.link_shown){
    $("linkShown").textContent = "🔗 " + q.link_shown;
    $("linkShown").classList.remove("hidden");
    $("peekBtn").classList.remove("hidden");
  } else {
    $("linkShown").classList.add("hidden");
    $("peekBtn").classList.add("hidden");
  }
  $("linkReal").classList.add("hidden");
  $("choices").classList.remove("hidden");
  $("feedback").classList.add("hidden");
}

function peek(){
  const q = questions[idx];
  if (!q.link_real) return;
  $("linkReal").textContent = "Real destination: " + q.link_real;
  $("linkReal").classList.remove("hidden");
}

async function answer(saysPhishing){
  if (answered) return;
  answered = true;
  const q = questions[idx];
  const res = await fetch("/api/answer", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({id: q.id, says_phishing: saysPhishing})
  });
  const r = await res.json();

  if (r.correct){
    score++;
  } else {
    const key = r.is_phish ? r.category : "False alarm on a real message";
    missed[key] = (missed[key] || 0) + 1;
  }

  peek();
  $("choices").classList.add("hidden");
  $("fbTitle").textContent = (r.correct ? "✅ Correct! " : "❌ Not quite. ") + "This was " + (r.is_phish ? "PHISHING" : "LEGIT");
  $("fbTitle").className = r.correct ? "good" : "bad";
  $("fbExplain").textContent = r.explanation;
  $("fbClueTitle").textContent = r.is_phish ? "Clues to spot next time:" : "Why it looks safe:";

  const list = $("fbClues");
  list.innerHTML = "";
  r.clues.forEach(function(c){
    const li = document.createElement("li");
    li.textContent = c;
    list.appendChild(li);
  });

  $("nextBtn").textContent = (idx === questions.length - 1) ? "See results" : "Next";
  $("feedback").classList.remove("hidden");
}

function next(){
  if (idx === questions.length - 1){
    showEnd();
  } else {
    idx++;
    showQuestion();
  }
}

function showEnd(){
  saveBest(level, score);
  $("quiz").classList.add("hidden");
  $("end").classList.remove("hidden");
  $("endScore").textContent = "You scored " + score + " / " + questions.length + "  (" + cap(level) + ")";

  let rating = "";
  if (score >= 7) rating = "🏆 Sharp eyes! You would spot most scams.";
  else if (score >= 5) rating = "👍 Decent, but stay careful with links and urgent messages.";
  else rating = "⚠️ You would likely get phished. Read the Learn page and try again.";
  $("endRating").textContent = rating;

  const b = loadBest(level);
  $("endBest").textContent = "Your best on " + cap(level) + ": " + (b === null ? "-" : b + "/8");

  const list = $("endMissed");
  list.innerHTML = "";
  const keys = Object.keys(missed);
  if (keys.length === 0){
    const li = document.createElement("li");
    li.textContent = "Nothing. Perfect round!";
    list.appendChild(li);
  } else {
    keys.forEach(function(k){
      const li = document.createElement("li");
      li.textContent = k + " (missed " + missed[k] + ")";
      list.appendChild(li);
    });
  }
}

document.querySelectorAll(".lvl").forEach(function(b){
  b.addEventListener("click", function(){ startRound(b.getAttribute("data-level")); });
});
$("againBtn").addEventListener("click", function(){
  $("end").classList.add("hidden");
  $("start").classList.remove("hidden");
  showBests();
});
$("peekBtn").addEventListener("click", peek);
$("btnPhish").addEventListener("click", function(){ answer(true); });
$("btnLegit").addEventListener("click", function(){ answer(false); });
$("nextBtn").addEventListener("click", next);

showBests();
</script>
</body>
</html>
"""

LEARN_PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>How to spot phishing</title>
<style>__STYLE__</style>
</head>
<body>
<div class="wrap">
  __NAV__
  <h1>📘 How to spot phishing</h1>
  <div class="sub">8 habits that stop most scams.</div>

  <div class="card">
    <ol>
      <li><b>Check the sender's address, not just the name.</b> Look for swapped characters: paypa1 (1 for l), acc0unts (0 for o), rnicrosoft (rn for m).</li>
      <li><b>Read the link before you click.</b> On a computer, hover over it. On a phone, press and hold. The real website is the end of the address, before the first "/". So in yourcompany.com.secure-login.net the real site is secure-login.net.</li>
      <li><b>Be careful when you feel rushed or scared.</b> "Blocked today", "24 hours", "fine doubles" are all pressure tricks.</li>
      <li><b>Watch for generic greetings.</b> "Dear customer" or "Dear user" often means mass-sent.</li>
      <li><b>Never share an OTP, PIN or password.</b> No bank or company needs them from you.</li>
      <li><b>Do not open unexpected attachments.</b> Especially .exe, .zip, or double extensions like .pdf.exe.</li>
      <li><b>If it sounds too good to be true, it is.</b> Real jobs and prizes never ask you to pay first.</li>
      <li><b>Verify another way.</b> Open the app yourself, type the website yourself, or call the number printed on your card.</li>
    </ol>
  </div>

  <div class="card">
    <h3>Already clicked or replied?</h3>
    <ol>
      <li>Do not enter anything else. Close the page.</li>
      <li>If you typed a password, change it now and turn on two-step verification.</li>
      <li>If you shared card or bank details, call your bank right away to block or freeze.</li>
      <li>Tell your IT team or a trusted person if it was a work or college account.</li>
      <li>Report it. In India, use cybercrime.gov.in or call 1930. Also use the "Report phishing" option in your email app.</li>
    </ol>
  </div>

  <a href="/"><button class="neutral">🎮 Test yourself</button></a>
</div>
</body>
</html>
"""

PAGE_HTML = PAGE.replace("__STYLE__", STYLE).replace("__NAV__", NAV)
LEARN_HTML = LEARN_PAGE.replace("__STYLE__", STYLE).replace("__NAV__", NAV)


@app.route("/")
def home():
    return Response(PAGE_HTML, mimetype="text/html")


@app.route("/learn")
def learn():
    return Response(LEARN_HTML, mimetype="text/html")


@app.route("/api/round")
def new_round():
    level = request.args.get("level", "easy")
    allowed = LEVELS.get(level, LEVELS["easy"])
    pool = [s for s in SCENARIOS if s["difficulty"] in allowed]
    phish = [s for s in pool if s["is_phish"]]
    legit = [s for s in pool if not s["is_phish"]]
    picked = random.sample(phish, min(5, len(phish))) + random.sample(legit, min(3, len(legit)))
    random.shuffle(picked)
    public = []
    for s in picked:
        public.append({k: s[k] for k in ("id", "channel", "sender", "subject", "body", "link_shown", "link_real")})
    return jsonify(public)


@app.route("/api/answer", methods=["POST"])
def check_answer():
    data = request.get_json() or {}
    s = next((x for x in SCENARIOS if x["id"] == data.get("id")), None)
    if s is None:
        return jsonify({"error": "unknown question"}), 404
    says_phishing = data.get("says_phishing") is True
    return jsonify({
        "correct": says_phishing == s["is_phish"],
        "is_phish": s["is_phish"],
        "category": s["category"],
        "clues": s["clues"],
        "explanation": s["explanation"],
    })


if __name__ == "__main__":
    app.run(debug=True)