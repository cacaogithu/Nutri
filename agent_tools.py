"""
Agent Tools - Capabilities available to all agents through the orchestrator.
"""
import os
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from database import db
from whatsapp_api import whatsapp

logger = logging.getLogger(__name__)

class AgentTools:
    """Tool registry for agent capabilities."""
    
    def __init__(self):
        self.tools = {
            "generate_pdf_plan": self.generate_pdf_plan,
            "send_pdf_via_whatsapp": self.send_pdf_via_whatsapp,
            "check_payment_status": self.check_payment_status,
            "escalate_to_human": self.escalate_to_human,
            "schedule_followup": self.schedule_followup,
        }
    
    def execute_tool(self, tool_name: str, phone: str, **kwargs) -> Dict:
        """Execute a tool and log the execution."""
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }
        
        try:
            input_data = {"phone": phone, **kwargs}
            result = self.tools[tool_name](phone, **kwargs)
            
            # Log execution
            db.log_tool_execution(
                phone=phone,
                tool_name=tool_name,
                input_data=input_data,
                output_data=result
            )
            
            return result
        except Exception as e:
            logger.error(f"Tool execution error: {tool_name} for {phone}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_pdf_plan(self, phone: str, plan_data: Dict) -> Dict:
        """
        Generate PDF diet plan.
        
        Args:
            phone: Client phone number
            plan_data: Plan data including meals, macros, etc.
        
        Returns:
            Dict with success status and file path
        """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.units import inch
            
            # Create PDFs directory
            pdfs_dir = "data/pdfs"
            os.makedirs(pdfs_dir, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"plan_{phone}_{timestamp}.pdf"
            filepath = os.path.join(pdfs_dir, filename)
            
            # Create PDF
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#2E7D32'),
                spaceAfter=30
            )
            story.append(Paragraph("Plano Nutricional Personalizado", title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Client info
            client = db.get_client(phone)
            if client:
                client_name = client.get('name', 'Cliente')
                story.append(Paragraph(f"<b>Cliente:</b> {client_name}", styles['Normal']))
                story.append(Paragraph(f"<b>Data:</b> {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
                story.append(Spacer(1, 0.3*inch))
            
            # Plan content
            plan_text = plan_data.get('plan_text', '')
            if plan_text:
                # Split by lines and add as paragraphs
                for line in plan_text.split('\n'):
                    if line.strip():
                        story.append(Paragraph(line.strip(), styles['Normal']))
                        story.append(Spacer(1, 0.1*inch))
            
            # Build PDF
            doc.build(story)
            
            # Save to database
            plan_id = plan_data.get('plan_id', f"plan_{phone}_{timestamp}")
            db.save_pdf_document(phone, plan_id, filepath)
            
            logger.info(f"✅ PDF generated: {filepath}")
            
            return {
                "success": True,
                "file_path": filepath,
                "plan_id": plan_id
            }
            
        except ImportError:
            # Fallback to simple text file if reportlab not available
            logger.warning("reportlab not available, creating text file instead")
            pdfs_dir = "data/pdfs"
            os.makedirs(pdfs_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"plan_{phone}_{timestamp}.txt"
            filepath = os.path.join(pdfs_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("PLANO NUTRICIONAL PERSONALIZADO\n")
                f.write("=" * 50 + "\n\n")
                f.write(plan_data.get('plan_text', ''))
            
            plan_id = plan_data.get('plan_id', f"plan_{phone}_{timestamp}")
            db.save_pdf_document(phone, plan_id, filepath)
            
            return {
                "success": True,
                "file_path": filepath,
                "plan_id": plan_id,
                "format": "txt"
            }
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_pdf_via_whatsapp(self, phone: str, pdf_path: str, caption: str = "Seu plano nutricional personalizado") -> Dict:
        """Send PDF via WhatsApp."""
        try:
            if not os.path.exists(pdf_path):
                return {
                    "success": False,
                    "error": f"File not found: {pdf_path}"
                }
            
            result = whatsapp.send_file(phone, pdf_path, caption)
            
            if result.get("success"):
                # Mark PDF as sent
                # Extract plan_id from path or use phone
                plan_id = os.path.basename(pdf_path).replace('.pdf', '').replace('.txt', '')
                db.mark_pdf_sent(phone, plan_id)
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending PDF: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def check_payment_status(self, phone: str) -> Dict:
        """Check subscription/payment status."""
        try:
            client = db.get_client(phone)
            if not client:
                return {
                    "success": False,
                    "error": "Client not found"
                }
            
            client_id = f"client_{phone}"
            subscription = db._load().get("subscriptions", {}).get(client_id)
            
            if subscription:
                return {
                    "success": True,
                    "status": subscription.get("status", "unknown"),
                    "price": subscription.get("price", 0),
                    "started_at": subscription.get("started_at"),
                    "active": subscription.get("status") == "active"
                }
            else:
                return {
                    "success": True,
                    "status": "no_subscription",
                    "active": False
                }
                
        except Exception as e:
            logger.error(f"Error checking payment status: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def escalate_to_human(self, phone: str, reason: str = "Agent requested escalation") -> Dict:
        """Escalate conversation to human support."""
        try:
            from message_router import router
            
            success = router.escalate_to_human(phone, reason)
            
            if success:
                db.create_alert(
                    type='human_escalation',
                    phone=phone,
                    details=f"Escalated: {reason}"
                )
            
            return {
                "success": success,
                "message": "Escalated to human support" if success else "Escalation failed"
            }
            
        except Exception as e:
            logger.error(f"Error escalating: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def schedule_followup(self, phone: str, delay_hours: int, message: str) -> Dict:
        """
        Schedule a follow-up message.
        
        Note: This is a placeholder. In production, you'd use a task queue
        like Celery or a cron job to send scheduled messages.
        """
        try:
            followup_time = datetime.now() + timedelta(hours=delay_hours)
            
            # Store in database for later processing
            # In production, add to a scheduled_messages table
            db.create_alert(
                type='scheduled_followup',
                phone=phone,
                details=f"Scheduled for {followup_time.isoformat()}: {message}"
            )
            
            return {
                "success": True,
                "scheduled_for": followup_time.isoformat(),
                "message": "Follow-up scheduled (requires task queue for execution)"
            }
            
        except Exception as e:
            logger.error(f"Error scheduling followup: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Global instance
agent_tools = AgentTools()


