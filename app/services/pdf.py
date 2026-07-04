# app/services/pdf.py
from io import BytesIO
from xhtml2pdf import pisa
from app.interfaces import PDFGenerator
from app.models import CompanyInfo, CompetitorInfo

class XhtmlPdfGenerator(PDFGenerator):
    async def generate_report(self, company_info: CompanyInfo, competitors: list[CompetitorInfo]) -> bytes:
        pdf_buffer = BytesIO()
        
        products_html = "".join([f"<li>{p}</li>" for p in company_info.products_services])
        pain_points_html = "".join([f"<li>{p}</li>" for p in company_info.pain_points])
        
        competitors_html = "".join([
            f"<tr><td><strong>{c.name}</strong></td><td><a href='{c.website}'>{c.website}</a></td></tr>"
            for c in competitors
        ])

        html_template = f"""
        <html>
        <head>
            <style>
                @page {{ size: letter; margin: 1in; }}
                body {{ font-family: Helvetica, Arial, sans-serif; color: #333333; line-height: 1.4; }}
                h1 {{ color: #1e3a8a; font-size: 24pt; margin-bottom: 5px; }}
                h2 {{ color: #2563eb; font-size: 16pt; border-bottom: 1px solid #e5e7eb; padding-bottom: 5px; margin-top: 20px; }}
                .metadata {{ font-size: 10pt; color: #6b7280; margin-bottom: 20px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #e5e7eb; }}
                th {{ background-color: #f3f4f6; color: #1f2937; }}
                ul {{ margin-top: 5px; padding-left: 20px; }}
                li {{ margin-bottom: 4px; }}
            </style>
        </head>
        <body>
            <h1>Strategic Intelligence Report</h1>
            <div class="metadata">Target: {company_info.name} | Base Domain: {company_info.website}</div>
            
            <h2>Company Profile</h2>
            <p><strong>HQ Address:</strong> {company_info.address or 'Not Provided'}</p>
            <p><strong>Contact Phone:</strong> {company_info.phone or 'Not Provided'}</p>
            
            <h2>Core Offerings & Capabilities</h2>
            <ul>{products_html or '<li>No explicitly itemized offerings found.</li>'}</ul>
            
            <h2>AI-Identified Operational Pain Points</h2>
            <ul>{pain_points_html or '<li>No major operational vulnerabilities mapped.</li>'}</ul>
            
            <h2>Competitive Matrix</h2>
            <table>
                <thead>
                    <tr>
                        <th>Competitor Organization</th>
                        <th>Digital Flagship Domain</th>
                    </tr>
                </thead>
                <tbody>
                    {competitors_html or '<tr><td colspan="2">No key competitor vectors found.</td></tr>'}
                </tbody>
            </table>
        </body>
        </html>
        """
        
        pisa_status = pisa.CreatePDF(html_template, dest=pdf_buffer)
        if pisa_status.err:
            raise RuntimeError("Internal PDF Engine Render Error Occurred.")
            
        return pdf_buffer.getvalue()