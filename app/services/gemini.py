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
