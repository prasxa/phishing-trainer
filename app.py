from flask import Flask, jsonify, request, Response
import random

app = Flask(__name__)

SCENARIOS = [
    {
        "id": 1, "channel": "Email",
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
        "id": 2, "channel": "Email",
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
        "id": 3, "channel": "SMS",
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
        "id": 4, "channel": "Email",
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
        "id": 5, "channel": "Email",
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
        "id": 6, "channel": "Email",
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
        "id": 7, "channel": "WhatsApp",
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
        "id": 8, "channel": "SMS",
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
        "id": 9, "channel": "SMS",
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
        "id": 10, "channel": "Email",
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
        "id": 11, "channel": "Email",
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
        "id": 12, "channel": "Email",
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
]

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Would I Fall For It?</title>
<style>
  body{font-family:Segoe UI,Arial,sans-serif;background:#0f172a;color:#e2e8f0;margin:0;padding:24px;}
  .wrap{max-width:680px;margin:0 auto;}
  h1{margin:0 0 4px;}
  .sub{color:#94a3b8;margin-bottom:20px;}
  .card{background:#1e293b;border-radius:12px;padding:20px;margin-bottom:16px;}
  .meta{color:#94a3b8;font-size:14px;margin:2px 0;}
  .body{white-space:pre-wrap;margin:14px 0;line-height:1.5;}
  button{font-size:16px;padding:10px 18px;border:0;border-radius:8px;cursor:pointer;margin-right:8px;color:#fff;}
  .phish{background:#dc2626;}
  .legit{background:#16a34a;}
  .neutral{background:#3b82f6;}
  .peek{background:#475569;font-size:14px;padding:6px 12px;margin-top:8px;}
  .link{font-family:Consolas,monospace;font-size:14px;margin-top:8px;}
  .real{color:#fbbf24;}
  .good{color:#4ade80;}
  .bad{color:#f87171;}
  .hidden{display:none;}
  ul{padding-left:20px;line-height:1.6;}
</style>
</head>
<body>
<div class="wrap">
  <h1>🎣 Would I Fall For It?</h1>
  <div class="sub">Read the message. Is it phishing or legit?</div>

  <div id="start" class="card">
    <p>You will see 8 messages. Decide if each one is a phishing attempt or a real message.</p>
    <button class="neutral" id="startBtn">Start</button>
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
    <div class="meta" style="margin-top:12px;">Where you slipped:</div>
    <ul id="endMissed"></ul>
    <button class="neutral" id="againBtn">Play again</button>
  </div>
</div>

<script>
let questions = [];
let idx = 0;
let score = 0;
let missed = {};
let answered = false;

function $(id){ return document.getElementById(id); }

async function startRound(){
  const res = await fetch("/api/round");
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
  $("progress").textContent = "Question " + (idx + 1) + " of " + questions.length + "   |   Score: " + score;
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
  $("quiz").classList.add("hidden");
  $("end").classList.remove("hidden");
  $("endScore").textContent = "You scored " + score + " / " + questions.length;

  let rating = "";
  if (score >= 7) rating = "🏆 Sharp eyes! You would spot most scams.";
  else if (score >= 5) rating = "👍 Decent, but stay careful with links and urgent messages.";
  else rating = "⚠️ You would likely get phished. Review the clues and try again.";
  $("endRating").textContent = rating;

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

$("startBtn").addEventListener("click", startRound);
$("againBtn").addEventListener("click", startRound);
$("peekBtn").addEventListener("click", peek);
$("btnPhish").addEventListener("click", function(){ answer(true); });
$("btnLegit").addEventListener("click", function(){ answer(false); });
$("nextBtn").addEventListener("click", next);
</script>
</body>
</html>
"""


@app.route("/")
def home():
    return Response(PAGE, mimetype="text/html")


@app.route("/api/round")
def new_round():
    phish = [s for s in SCENARIOS if s["is_phish"]]
    legit = [s for s in SCENARIOS if not s["is_phish"]]
    picked = random.sample(phish, 5) + random.sample(legit, 3)
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