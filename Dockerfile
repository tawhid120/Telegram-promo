# Python 3.11 এর লাইটওয়েট ভার্সন ব্যবহার করা হচ্ছে (pyrofork এর জন্য আপডেট করা হলো)
FROM python:3.11-slim

# কাজের ডিরেক্টরি সেট করা
WORKDIR /app

# রিকোয়ারমেন্টস কপি করে ইনস্টল করা
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# প্রজেক্টের বাকি সব ফাইল কপি করা
COPY . .

# Flask সার্ভারের পোর্ট এক্সপোজ করা
EXPOSE 5000

# অ্যাপ রান করার কমান্ড (web.py রান করলেই সে main.py কে চালু করে দেবে)
CMD ["python", "web.py"]
