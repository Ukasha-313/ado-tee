import json
import re
from datetime import datetime, timedelta, timezone


class AIEngine:
    """
    Lightweight local AI-style reasoning layer.
    Replace `analyze_document()` with an LLM API later if desired.
    """

    def analyze_document(self, file_name, text):
        category = self.classify(file_name, text)
        summary = self.summarize(text)
        deadlines = self.extract_deadlines(text)
        priority = self.calculate_priority(deadlines)

        return {
            "category": category,
            "summary": summary,
            "deadlines": deadlines,
            "priority": priority,
            "ai_confidence": self.confidence(text)
        }

    def classify(self, file_name, text):
        blob = (file_name + " " + text[:6000]).lower()

        academic = ["assignment", "quiz", "lecture", "course", "exam",
                    "midterm", "syllabus", "lab task", "university"]
        financial = ["invoice", "bank", "statement", "salary", "tax", "receipt"]
        administrative = ["form", "challan", "application", "notice", "certificate"]
        code = [".py", ".js", ".java", ".cpp", "function", "import", "class"]

        scores = {
            "Academic": sum(blob.count(k) for k in academic),
            "Financial": sum(blob.count(k) for k in financial),
            "Administrative": sum(blob.count(k) for k in administrative),
            "Code": sum(blob.count(k) for k in code)
        }

        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else "General Document"

    def summarize(self, text):
        text = " ".join(text.split())

        if not text:
            return "No readable text found. OCR may be required."

        sentences = re.split(r"(?<=[.!?])\s+", text)

        important_words = [
            "assignment", "quiz", "exam", "deadline", "due",
            "submission", "invoice", "fee", "result", "notice"
        ]

        scored = []
        for sentence in sentences[:80]:
            score = sum(sentence.lower().count(word) for word in important_words)
            scored.append((score, sentence))

        scored.sort(reverse=True, key=lambda item: item[0])

        if not scored:
            return text[:220]

        return scored[0][1][:280]

    def extract_deadlines(self, text):
        deadlines = []

        patterns = [
            r"(?:due\s*(?:date|by)|deadline|submission\s*(?:date|deadline)|last\s*date)\s*[:\-]?\s*([^\n\r]{3,160})",
            r"(quiz\s*\d+|assignment\s*#?\s*\d+|lab\s*task\s*\d+|midterm|final\s*exam)[^\n\r]{0,180}"
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                raw = " ".join(match.group(0).split())[:260]
                exact_date = self.find_date(raw)

                deadlines.append({
                    "task": raw,
                    "detected_date": exact_date,
                    "priority": self.date_priority(exact_date)
                })

        return deadlines

    def find_date(self, text):
        patterns = [
            r"(\d{4}-\d{2}-\d{2})",
            r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            r"(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4})",
            r"((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2},?\s+\d{4})"
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def date_priority(self, date_text):
        if not date_text:
            return "Medium"

        try:
            parsed = datetime.strptime(date_text, "%Y-%m-%d")
        except ValueError:
            return "Medium"

        today = datetime.now().date()
        days_left = (parsed.date() - today).days

        if days_left < 0:
            return "Overdue"
        if days_left <= 2:
            return "Critical"
        if days_left <= 7:
            return "High"
        if days_left <= 30:
            return "Medium"
        return "Low"

    def calculate_priority(self, deadlines):
        if not deadlines:
            return "None"

        levels = ["Overdue", "Critical", "High", "Medium", "Low"]
        priorities = [item["priority"] for item in deadlines]

        for level in levels:
            if level in priorities:
                return level

        return "Medium"

    def confidence(self, text):
        if len(text) < 50:
            return 0.25
        if len(text) < 300:
            return 0.55
        return 0.85