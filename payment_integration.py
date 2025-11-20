"""
Payment Integration - Handles recurring subscriptions for R$47/month.
Supports multiple payment providers (Stripe, PagSeguro, etc.)
"""
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from database import db
from config import SUBSCRIPTION_PRICE

logger = logging.getLogger(__name__)

class PaymentIntegration:
    """Handles payment processing and subscription management."""
    
    def __init__(self):
        self.subscription_price = SUBSCRIPTION_PRICE
        # In production, initialize payment provider clients here
        # self.stripe_client = stripe.Client(api_key=STRIPE_API_KEY)
        # self.pagseguro_client = PagSeguroClient(...)
    
    def create_subscription(self, phone: str, payment_method: str = "manual") -> Dict:
        """
        Create a new subscription for a client.
        
        Args:
            phone: Client phone number
            payment_method: Payment method (stripe, pagseguro, manual)
        
        Returns:
            Dict with subscription details
        """
        try:
            client = db.get_client(phone)
            if not client:
                return {
                    "success": False,
                    "error": "Client not found"
                }
            
            client_id = f"client_{phone}"
            data = db._load()
            
            # Check if subscription already exists
            if client_id in data.get("subscriptions", {}):
                existing = data["subscriptions"][client_id]
                if existing.get("status") == "active":
                    return {
                        "success": True,
                        "message": "Subscription already active",
                        "subscription": existing
                    }
            
            # Create subscription
            subscription = {
                "client_id": client_id,
                "phone": phone,
                "price": self.subscription_price,
                "status": "active",
                "payment_method": payment_method,
                "started_at": datetime.now().isoformat(),
                "next_billing_date": (datetime.now() + timedelta(days=30)).isoformat(),
                "created_at": datetime.now().isoformat()
            }
            
            data.setdefault("subscriptions", {})[client_id] = subscription
            db._save(data)
            
            logger.info(f"✅ Subscription created for {phone}")
            
            return {
                "success": True,
                "subscription": subscription
            }
            
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def cancel_subscription(self, phone: str, reason: str = "") -> Dict:
        """Cancel a subscription."""
        try:
            client_id = f"client_{phone}"
            data = db._load()
            
            if client_id not in data.get("subscriptions", {}):
                return {
                    "success": False,
                    "error": "Subscription not found"
                }
            
            subscription = data["subscriptions"][client_id]
            subscription["status"] = "cancelled"
            subscription["cancelled_at"] = datetime.now().isoformat()
            subscription["cancellation_reason"] = reason
            
            db._save(data)
            
            logger.info(f"❌ Subscription cancelled for {phone}: {reason}")
            
            return {
                "success": True,
                "message": "Subscription cancelled"
            }
            
        except Exception as e:
            logger.error(f"Error cancelling subscription: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def process_payment_webhook(self, provider: str, payload: Dict) -> Dict:
        """
        Process payment webhook from payment provider.
        
        Args:
            provider: Payment provider (stripe, pagseguro)
            payload: Webhook payload
        
        Returns:
            Dict with processing result
        """
        try:
            # In production, verify webhook signature here
            
            event_type = payload.get("type", "")
            
            if provider == "stripe":
                return self._process_stripe_webhook(event_type, payload)
            elif provider == "pagseguro":
                return self._process_pagseguro_webhook(event_type, payload)
            else:
                return {
                    "success": False,
                    "error": f"Unknown provider: {provider}"
                }
                
        except Exception as e:
            logger.error(f"Error processing payment webhook: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _process_stripe_webhook(self, event_type: str, payload: Dict) -> Dict:
        """Process Stripe webhook."""
        # Placeholder - implement Stripe webhook handling
        logger.info(f"Stripe webhook: {event_type}")
        return {"success": True, "processed": True}
    
    def _process_pagseguro_webhook(self, event_type: str, payload: Dict) -> Dict:
        """Process PagSeguro webhook."""
        # Placeholder - implement PagSeguro webhook handling
        logger.info(f"PagSeguro webhook: {event_type}")
        return {"success": True, "processed": True}
    
    def get_subscription_status(self, phone: str) -> Dict:
        """Get subscription status for a phone number."""
        try:
            client_id = f"client_{phone}"
            data = db._load()
            subscription = data.get("subscriptions", {}).get(client_id)
            
            if subscription:
                return {
                    "success": True,
                    "subscription": subscription,
                    "active": subscription.get("status") == "active"
                }
            else:
                return {
                    "success": True,
                    "subscription": None,
                    "active": False
                }
                
        except Exception as e:
            logger.error(f"Error getting subscription status: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def check_upcoming_renewals(self, days_ahead: int = 7) -> list:
        """Get subscriptions that need renewal in the next N days."""
        try:
            data = db._load()
            subscriptions = data.get("subscriptions", {})
            
            upcoming = []
            cutoff_date = datetime.now() + timedelta(days=days_ahead)
            
            for sub in subscriptions.values():
                if sub.get("status") != "active":
                    continue
                
                next_billing = sub.get("next_billing_date")
                if next_billing:
                    billing_date = datetime.fromisoformat(next_billing)
                    if billing_date <= cutoff_date:
                        upcoming.append(sub)
            
            return sorted(upcoming, key=lambda x: x.get("next_billing_date", ""))
            
        except Exception as e:
            logger.error(f"Error checking renewals: {e}")
            return []

# Global instance
payment_integration = PaymentIntegration()


