import os
import json
import google.generativeai as genai
from app.config import settings
from app.schemas import OcrResponse

def analyze_receipt_with_gemini(file_content: bytes, mime_type: str) -> dict:
    # 1. Fallback if key is missing or dummy
    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your_gemini_api_key_here":
        print("Gemini API key is not configured. Running OCR simulation fallback.")
        return {
            "merchantName": "Target Stores",
            "transactionDate": "18 Jun 2026",
            "invoiceNumber": "INV-2026-8849",
            "category": "Office Supplies",
            "paymentMethod": "Credit Card",
            "taxId": "US-7766554-1",
            "notes": "Extracted via local simulation. Set GEMINI_API_KEY in .env for real OCR.",
            "itemsList": "1x Wireless Keyboard (₹45.00)\n2x AA Battery Pack (₹15.00)\n1x USB-C Charger (₹25.00)",
            "subtotal": "₹85.00",
            "taxAmount": "₹6.80",
            "totalAmount": "₹91.80",
            "discount": "₹0.00",
            "cardEnding": "Visa *9981"
        }

    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Using gemini-2.5-flash for OCR & fast analysis
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = (
            "Analyze this receipt image or PDF and extract the required details. "
            "Return a JSON object exactly matching the requested schema. "
            "All monetary currency symbols must be normalized to '₹' (e.g. ₹120.00, ₹5.50). "
            "Under itemsList, list all purchased items, one per line with quantity, name and price (e.g. '1x Laptop Stand (₹299.00)')."
        )
        
        # Prepare multimodal file input
        file_part = {
            "mime_type": mime_type,
            "data": file_content
        }
        
        response = model.generate_content(
            [prompt, file_part],
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
                response_schema=OcrResponse
            )
        )
        
        return json.loads(response.text)
    except Exception as e:
        print(f"Gemini API execution error: {e}. Falling back to simulation.")
        return {
            "merchantName": "Fallback Extracted Store",
            "transactionDate": "Today",
            "invoiceNumber": "INV-2026-ERR",
            "category": "Others",
            "paymentMethod": "Cash",
            "taxId": "None",
            "notes": f"Gemini call failed: {str(e)}",
            "itemsList": "1x Fallback Item (₹100.00)",
            "subtotal": "₹100.00",
            "taxAmount": "₹0.00",
            "totalAmount": "₹100.00",
            "discount": "₹0.00",
            "cardEnding": "None (Cash)"
        }

def generate_insights_with_gemini(expenses_summary: dict) -> list:
    # 1. Fallback if key is missing or dummy
    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your_gemini_api_key_here":
        print("Gemini API key is not configured for insights. Running rule-based fallback.")
        return generate_rule_based_insights(expenses_summary)

    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = (
            f"You are a helpful financial AI assistant. Analyze this financial summary for the user:\n"
            f"- Total spent: ₹{expenses_summary['total_spent']:.2f}\n"
            f"- Number of transactions: {expenses_summary['count']}\n"
            f"- Category Breakdown: {expenses_summary['categories']}\n"
            f"- Top Category: {expenses_summary['top_category']} (spent ₹{expenses_summary['top_category_amount']:.2f})\n\n"
            "Based on this data, write exactly 3 short, punchy, actionable financial insights/recommendations "
            "for the user. Each insight must be a single sentence of maximum 55 characters. Do not use markdown. "
            "Return a JSON array of 3 strings, e.g. [\"You spent 15% less this week on food.\", ...]."
        )
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Gemini insights generation error: {e}. Falling back to rule-based insights.")
        return generate_rule_based_insights(expenses_summary)

def generate_rule_based_insights(expenses_summary: dict) -> list:
    total = expenses_summary["total_spent"]
    count = expenses_summary["count"]
    top_cat = expenses_summary["top_category"]
    top_cat_amt = expenses_summary["top_category_amount"]
    
    if count == 0:
        return [
            "Welcome! Upload your first receipt to see smart insights.",
            "Start tracking your budget to identify potential savings.",
            "Scan bills to extract details instantly with Gemini OCR."
        ]
    
    insights = []
    insights.append(f"Total spent so far is ₹{total:,.2f} across {count} transactions.")
    
    if top_cat and top_cat != "None":
        pct = (top_cat_amt / total * 100) if total > 0 else 0
        insights.append(f"Your top category is {top_cat}, consuming {pct:.0f}% of spend.")
    else:
        insights.append("Keep logging expenses to see category breakdowns.")
        
    if total > 5000:
        insights.append("Consider setting a daily limit to manage high spending.")
    else:
        insights.append("Good job! Your current budget looks well-controlled.")
        
    return insights

