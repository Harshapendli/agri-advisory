from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, List
from rag.graphrag_chain import run_graphrag, run_chat_query
from models.advisory import Advisory, ChatMessage
from routers.auth import get_current_user
from models.user import User
import io
from datetime import datetime

router = APIRouter(prefix="/advisory", tags=["advisory"])

class AdvisoryRequest(BaseModel):
    query: str
    soil: Optional[Dict[str, float]] = None
    location: str = "Hyderabad"
    language: str = "en"

class ChatRequest(BaseModel):
    query: str
    location: str = "Hyderabad"
    language: str = "en"
    history: Optional[List[Dict[str, str]]] = None

@router.post("")
async def get_advisory(req: AdvisoryRequest):
    result = await run_graphrag(
        query=req.query,
        soil_params=req.soil,
        location=req.location,
        language=req.language
    )
    advisory_text = str(result.get("advisory", {}).get("recommendation", ""))
    doc = Advisory(
        user_id=None,
        query=req.query,
        response=advisory_text,
        recommended_crop=result.get("ml_prediction", {}).get("predicted_crop"),
        confidence=result.get("ml_prediction", {}).get("confidence"),
        shap_factors=result.get("shap_factors", []),
        language=req.language,
        sources=result.get("sources", [])
    )
    await doc.insert()
    return {**result, "advisory_id": str(doc.id)}

@router.post("/chat")
async def chat_advisory(req: ChatRequest):
    """Conversational chat endpoint - answers the user's actual question
    using OpenAI + weather + knowledge graph, without forcing ML prediction."""
    result = await run_chat_query(
        query=req.query,
        location=req.location,
        language=req.language,
        history=req.history or []
    )

    # Save chat conversation to MongoDB
    try:
        doc = ChatMessage(
            query=req.query,
            answer=result.get("answer", ""),
            location=req.location,
            detected_location=result.get("location"),
            language=req.language,
            sources=result.get("sources", [])
        )
        await doc.insert()
        result["chat_id"] = str(doc.id)
    except Exception as e:
        print(f"Failed to save chat message: {e}")

    return result

@router.get("/history")
async def get_history(current_user: User = Depends(get_current_user), limit: int = 20):
    advisories = await Advisory.find(Advisory.user_id == current_user.id).sort("-created_at").limit(limit).to_list()
    return [{"id": str(a.id), "query": a.query, "recommended_crop": a.recommended_crop,
             "confidence": a.confidence, "language": a.language, "created_at": a.created_at} for a in advisories]

@router.get("/chat-history")
async def get_chat_history(limit: int = 20):
    """Get recent chat conversations."""
    chats = await ChatMessage.find().sort("-created_at").limit(limit).to_list()
    return [{"id": str(c.id), "query": c.query, "answer": c.answer[:150] + "..." if len(c.answer) > 150 else c.answer,
             "location": c.detected_location or c.location, "language": c.language,
             "created_at": c.created_at} for c in chats]


class PDFExportRequest(BaseModel):
    crop: str
    confidence: float
    location: str
    advisory: Optional[Dict] = None
    shap_factors: Optional[List[Dict]] = None
    weather: Optional[Dict] = None

@router.post("/export-pdf")
async def export_advisory_pdf(req: PDFExportRequest):
    """Generate a downloadable PDF report of the advisory."""
    try:
        from fpdf import FPDF
    except ImportError:
        # Fallback to HTML-based report if fpdf not installed
        html = _generate_html_report(req)
        return StreamingResponse(
            io.BytesIO(html.encode('utf-8')),
            media_type="text/html",
            headers={"Content-Disposition": f'attachment; filename="AgriAdvisory_Report_{req.crop}_{datetime.now().strftime("%Y%m%d")}.html"'}
        )

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Header
    pdf.set_fill_color(34, 139, 34)
    pdf.rect(0, 0, 210, 35, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 20)
    pdf.cell(0, 15, 'AgriAdvisory Report', ln=True, align='C')
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 8, f'Generated on {datetime.now().strftime("%d %B %Y, %I:%M %p")}', ln=True, align='C')
    pdf.ln(15)

    pdf.set_text_color(0, 0, 0)

    # Crop Prediction
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, f'Recommended Crop: {req.crop}', ln=True)
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 8, f'Confidence: {req.confidence:.1f}% | Location: {req.location}', ln=True)
    pdf.ln(5)

    # Weather
    if req.weather:
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 10, 'Weather Conditions', ln=True)
        pdf.set_font('Helvetica', '', 10)
        pdf.cell(0, 7, f'Temperature: {req.weather.get("temp", "N/A")} C | Humidity: {req.weather.get("humidity", "N/A")}%', ln=True)
        pdf.cell(0, 7, f'Conditions: {req.weather.get("description", "N/A")} | Wind: {req.weather.get("wind_speed", "N/A")} km/h', ln=True)
        pdf.ln(5)

    # Advisory sections
    adv = req.advisory or {}
    sections = [
        ('Crop Advice', adv.get('crop_advice')),
        ('Weather Advisory', adv.get('weather_advisory')),
        ('Irrigation Advice', adv.get('irrigation_advice')),
        ('Pest Control', adv.get('pest_control')),
        ('Market Outlook', adv.get('market_outlook')),
        ('Seasonal Tips', adv.get('seasonal_tips')),
    ]
    for title, content in sections:
        if content:
            pdf.set_font('Helvetica', 'B', 12)
            pdf.cell(0, 10, title, ln=True)
            pdf.set_font('Helvetica', '', 10)
            pdf.multi_cell(0, 6, content)
            pdf.ln(3)

    # Fertilizer Plan
    fert = adv.get('fertilizer_plan', [])
    if fert:
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 10, 'Fertilizer Plan', ln=True)
        pdf.set_font('Helvetica', '', 10)
        for f in fert:
            pdf.cell(0, 7, f'  - {f.get("fertilizer", "")}: {f.get("dose", "")} ({f.get("timing", "")})', ln=True)
        pdf.ln(3)

    # SHAP Factors
    if req.shap_factors:
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 10, 'Key Prediction Factors (SHAP)', ln=True)
        pdf.set_font('Helvetica', '', 10)
        for f in req.shap_factors[:5]:
            label = f.get('feature_label', f.get('feature', ''))
            imp = f.get('shap_importance', 0)
            val = f.get('value', '')
            pdf.cell(0, 7, f'  - {label}: {val} (importance: {imp:.4f})', ln=True)

    # Footer
    pdf.ln(10)
    pdf.set_font('Helvetica', 'I', 8)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 5, 'Generated by AgriAdvisory - AI-Powered Farming Intelligence', ln=True, align='C')
    pdf.cell(0, 5, 'Powered by XGBoost ML + Neo4j Knowledge Graph + OpenAI GPT', ln=True, align='C')

    pdf_bytes = pdf.output()
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="AgriAdvisory_{req.crop}_{datetime.now().strftime("%Y%m%d")}.pdf"'}
    )


def _generate_html_report(req) -> str:
    """Fallback HTML report when fpdf is not installed."""
    adv = req.advisory or {}
    weather = req.weather or {}
    now = datetime.now().strftime("%d %B %Y, %I:%M %p")

    sections_html = ""
    for title, content in [('Crop Advice', adv.get('crop_advice')), ('Weather Advisory', adv.get('weather_advisory')),
                            ('Irrigation', adv.get('irrigation_advice')), ('Pest Control', adv.get('pest_control')),
                            ('Market Outlook', adv.get('market_outlook')), ('Seasonal Tips', adv.get('seasonal_tips'))]:
        if content:
            sections_html += f'<h3 style="color:#166534;margin-top:16px;">{title}</h3><p>{content}</p>'

    fert_html = ""
    for f in adv.get('fertilizer_plan', []):
        fert_html += f'<tr><td style="padding:6px;border:1px solid #ddd;">{f.get("fertilizer","")}</td><td style="padding:6px;border:1px solid #ddd;">{f.get("dose","")}</td><td style="padding:6px;border:1px solid #ddd;">{f.get("timing","")}</td></tr>'

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>AgriAdvisory Report - {req.crop}</title>
<style>body{{font-family:Arial,sans-serif;max-width:800px;margin:0 auto;padding:20px;color:#333}}
h1{{color:white;background:#166534;padding:20px;border-radius:12px;text-align:center}}
h2{{color:#166534;border-bottom:2px solid #166534;padding-bottom:8px}}
.meta{{background:#f0fdf4;padding:12px;border-radius:8px;margin:16px 0}}
table{{border-collapse:collapse;width:100%}}th{{background:#166534;color:white;padding:8px;text-align:left}}</style></head>
<body><h1>AgriAdvisory Report</h1><p style="text-align:center;color:#666;">Generated on {now}</p>
<div class="meta"><strong>Recommended Crop:</strong> {req.crop} ({req.confidence:.1f}% confidence)<br>
<strong>Location:</strong> {req.location}<br>
<strong>Weather:</strong> {weather.get('temp','N/A')}°C, {weather.get('humidity','N/A')}% humidity, {weather.get('description','N/A')}</div>
{sections_html}
{'<h2>Fertilizer Plan</h2><table><tr><th>Fertilizer</th><th>Dose</th><th>Timing</th></tr>' + fert_html + '</table>' if fert_html else ''}
<hr style="margin-top:30px;"><p style="text-align:center;color:#999;font-size:12px;">AgriAdvisory — AI-Powered Farming Intelligence<br>XGBoost ML + Neo4j Knowledge Graph + OpenAI GPT</p></body></html>"""
