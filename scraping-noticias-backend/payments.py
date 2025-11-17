"""
Sistema de Pagos - Yape, PayPal, Stripe
Maneja la integración con diferentes métodos de pago
"""

import qrcode
import io
import base64
from typing import Dict, Optional
from datetime import datetime
import json

# Importar SDKs de pago (se instalarán después)
try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    print("⚠️ Stripe SDK no disponible. Instala con: pip install stripe")

try:
    import paypalrestsdk
    PAYPAL_AVAILABLE = True
except ImportError:
    PAYPAL_AVAILABLE = False
    print("⚠️ PayPal SDK no disponible. Instala con: pip install paypalrestsdk")


# ==================== CONFIGURACIÓN ====================

class PaymentConfig:
    """Configuración de métodos de pago"""
    
    # YAPE (Perú)
    YAPE_NUMERO = "960899657"  # ⚠️ CAMBIA ESTO por tu número de Yape
    YAPE_NOMBRE = "Omar condori"  # ⚠️ CAMBIA ESTO
    
    # STRIPE
    STRIPE_SECRET_KEY = "sk_test_..."  # ⚠️ CAMBIA ESTO por tu clave secreta de Stripe
    STRIPE_PUBLISHABLE_KEY = "pk_test_..."  # ⚠️ CAMBIA ESTO
    STRIPE_WEBHOOK_SECRET = "whsec_..."  # ⚠️ CAMBIA ESTO
    
    # PAYPAL
    PAYPAL_MODE = "sandbox"  # "sandbox" para pruebas, "live" para producción
    PAYPAL_CLIENT_ID = "..."  # ⚠️ CAMBIA ESTO
    PAYPAL_CLIENT_SECRET = "..."  # ⚠️ CAMBIA ESTO
    
    # URLs de retorno
    SUCCESS_URL = "http://localhost:3000/pago/exitoso"
    CANCEL_URL = "http://localhost:3000/pago/cancelado"
    WEBHOOK_URL = "http://localhost:8001/api/v1/pagos/webhook"


# ==================== YAPE ====================

class YapePayment:
    """Gestor de pagos con Yape"""
    
    def __init__(self):
        self.numero = PaymentConfig.YAPE_NUMERO
        self.nombre = PaymentConfig.YAPE_NOMBRE
    
    def generar_qr(self, monto: float, plan_nombre: str, pago_id: int) -> Dict:
        """
        Genera un código QR para pago con Yape
        
        Args:
            monto: Monto a pagar
            plan_nombre: Nombre del plan
            pago_id: ID del pago en la base de datos
        
        Returns:
            Dict con la imagen QR en base64 y detalles del pago
        """
        try:
            # Formato de datos para Yape
            # En producción real, Yape tiene un formato específico
            # Este es un ejemplo simplificado
            datos_yape = {
                'numero': self.numero,
                'monto': f'S/ {monto:.2f}',
                'concepto': f'Suscripción {plan_nombre}',
                'referencia': f'PAY-{pago_id}'
            }
            
            # Crear string para QR
            qr_text = f"""
YAPE - {self.nombre}
Número: {datos_yape['numero']}
Monto: {datos_yape['monto']}
Concepto: {datos_yape['concepto']}
Referencia: {datos_yape['referencia']}

IMPORTANTE: Envía la captura de pantalla del comprobante
            """
            
            # Generar QR
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_text)
            qr.make(fit=True)
            
            # Crear imagen
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convertir a base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            return {
                'success': True,
                'qr_base64': img_base64,
                'numero_yape': self.numero,
                'monto': monto,
                'referencia': f'PAY-{pago_id}',
                'instrucciones': [
                    '1. Abre tu app de Yape',
                    f'2. Escanea el código QR o envía S/ {monto:.2f} al número {self.numero}',
                    f'3. En el concepto escribe: PAY-{pago_id}',
                    '4. Toma una captura de pantalla del comprobante',
                    '5. Sube la captura para verificar tu pago'
                ]
            }
            
        except Exception as e:
            print(f"❌ Error generando QR Yape: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verificar_pago(self, referencia: str, comprobante_img: Optional[str] = None) -> Dict:
        """
        Verifica un pago de Yape (requiere verificación manual)
        
        Args:
            referencia: Referencia del pago (PAY-XXX)
            comprobante_img: Imagen del comprobante en base64 (opcional)
        
        Returns:
            Dict con el resultado de la verificación
        """
        # En producción real, aquí iría la lógica de verificación
        # Por ahora, requiere verificación manual por un admin
        return {
            'success': True,
            'estado': 'pendiente_verificacion',
            'mensaje': 'Pago registrado. Un administrador verificará tu comprobante en las próximas 24 horas.',
            'requiere_verificacion_manual': True
        }


# ==================== PAYPAL ====================

class PayPalPayment:
    """Gestor de pagos con PayPal"""
    
    def __init__(self):
        if not PAYPAL_AVAILABLE:
            raise Exception("PayPal SDK no está instalado. Instala con: pip install paypalrestsdk")
        
        # Configurar PayPal
        paypalrestsdk.configure({
            "mode": PaymentConfig.PAYPAL_MODE,
            "client_id": PaymentConfig.PAYPAL_CLIENT_ID,
            "client_secret": PaymentConfig.PAYPAL_CLIENT_SECRET
        })
    
    def crear_pago(self, monto: float, plan_nombre: str, plan_id: int, user_email: str) -> Dict:
        """
        Crea un pago con PayPal
        
        Args:
            monto: Monto a pagar en USD
            plan_nombre: Nombre del plan
            plan_id: ID del plan
            user_email: Email del usuario
        
        Returns:
            Dict con la URL de aprobación y detalles del pago
        """
        try:
            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "redirect_urls": {
                    "return_url": PaymentConfig.SUCCESS_URL,
                    "cancel_url": PaymentConfig.CANCEL_URL
                },
                "transactions": [{
                    "item_list": {
                        "items": [{
                            "name": f"Suscripción {plan_nombre}",
                            "sku": f"PLAN-{plan_id}",
                            "price": f"{monto:.2f}",
                            "currency": "USD",
                            "quantity": 1
                        }]
                    },
                    "amount": {
                        "total": f"{monto:.2f}",
                        "currency": "USD"
                    },
                    "description": f"Suscripción al plan {plan_nombre}"
                }]
            })
            
            if payment.create():
                # Obtener URL de aprobación
                for link in payment.links:
                    if link.rel == "approval_url":
                        return {
                            'success': True,
                            'payment_id': payment.id,
                            'approval_url': str(link.href),
                            'estado': 'created'
                        }
            else:
                return {
                    'success': False,
                    'error': payment.error
                }
                
        except Exception as e:
            print(f"❌ Error creando pago PayPal: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def ejecutar_pago(self, payment_id: str, payer_id: str) -> Dict:
        """
        Ejecuta un pago después de la aprobación del usuario
        
        Args:
            payment_id: ID del pago de PayPal
            payer_id: ID del pagador
        
        Returns:
            Dict con el resultado de la ejecución
        """
        try:
            payment = paypalrestsdk.Payment.find(payment_id)
            
            if payment.execute({"payer_id": payer_id}):
                return {
                    'success': True,
                    'payment_id': payment_id,
                    'estado': 'completado',
                    'transaccion_id': payment.transactions[0].related_resources[0].sale.id
                }
            else:
                return {
                    'success': False,
                    'error': payment.error
                }
                
        except Exception as e:
            print(f"❌ Error ejecutando pago PayPal: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verificar_webhook(self, webhook_data: Dict) -> Dict:
        """
        Verifica un webhook de PayPal
        
        Args:
            webhook_data: Datos del webhook
        
        Returns:
            Dict con la información del evento
        """
        try:
            event_type = webhook_data.get('event_type')
            resource = webhook_data.get('resource', {})
            
            if event_type == 'PAYMENT.SALE.COMPLETED':
                return {
                    'success': True,
                    'evento': 'pago_completado',
                    'payment_id': resource.get('parent_payment'),
                    'transaccion_id': resource.get('id'),
                    'monto': resource.get('amount', {}).get('total'),
                    'estado': 'completado'
                }
            
            return {
                'success': True,
                'evento': event_type,
                'resource': resource
            }
            
        except Exception as e:
            print(f"❌ Error verificando webhook PayPal: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# ==================== STRIPE ====================

class StripePayment:
    """Gestor de pagos con Stripe"""
    
    def __init__(self):
        if not STRIPE_AVAILABLE:
            raise Exception("Stripe SDK no está instalado. Instala con: pip install stripe")
        
        # Configurar Stripe
        stripe.api_key = PaymentConfig.STRIPE_SECRET_KEY
    
    def crear_sesion_checkout(self, monto: float, plan_nombre: str, plan_id: int, 
                             user_email: str, pago_id: int) -> Dict:
        """
        Crea una sesión de checkout de Stripe
        
        Args:
            monto: Monto a pagar en USD
            plan_nombre: Nombre del plan
            plan_id: ID del plan
            user_email: Email del usuario
            pago_id: ID del pago en la base de datos
        
        Returns:
            Dict con la URL de checkout y detalles de la sesión
        """
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f'Suscripción {plan_nombre}',
                            'description': f'Plan {plan_nombre} - Scraping de Noticias',
                        },
                        'unit_amount': int(monto * 100),  # Stripe usa centavos
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f'{PaymentConfig.SUCCESS_URL}?session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url=PaymentConfig.CANCEL_URL,
                customer_email=user_email,
                metadata={
                    'plan_id': str(plan_id),
                    'pago_id': str(pago_id)
                }
            )
            
            return {
                'success': True,
                'session_id': session.id,
                'checkout_url': session.url,
                'estado': 'created'
            }
            
        except stripe.error.StripeError as e:
            print(f"❌ Error Stripe: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            print(f"❌ Error creando sesión Stripe: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verificar_sesion(self, session_id: str) -> Dict:
        """
        Verifica el estado de una sesión de checkout
        
        Args:
            session_id: ID de la sesión
        
        Returns:
            Dict con el estado de la sesión
        """
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            
            return {
                'success': True,
                'session_id': session_id,
                'payment_status': session.payment_status,
                'customer_email': session.customer_email,
                'metadata': session.metadata,
                'payment_intent': session.payment_intent
            }
            
        except stripe.error.StripeError as e:
            print(f"❌ Error Stripe: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verificar_webhook(self, payload: bytes, sig_header: str) -> Dict:
        """
        Verifica un webhook de Stripe
        
        Args:
            payload: Cuerpo del webhook (bytes)
            sig_header: Header de firma del webhook
        
        Returns:
            Dict con la información del evento
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, PaymentConfig.STRIPE_WEBHOOK_SECRET
            )
            
            if event.type == 'checkout.session.completed':
                session = event.data.object
                
                return {
                    'success': True,
                    'evento': 'pago_completado',
                    'session_id': session.id,
                    'payment_intent': session.payment_intent,
                    'customer_email': session.customer_email,
                    'metadata': session.metadata,
                    'monto': session.amount_total / 100,  # Convertir de centavos
                    'estado': 'completado'
                }
            
            return {
                'success': True,
                'evento': event.type,
                'data': event.data.object
            }
            
        except stripe.error.SignatureVerificationError as e:
            print(f"❌ Firma inválida del webhook Stripe: {e}")
            return {
                'success': False,
                'error': 'Firma inválida'
            }
        except Exception as e:
            print(f"❌ Error verificando webhook Stripe: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# ==================== FACTORY ====================

class PaymentFactory:
    """Factory para crear instancias de procesadores de pago"""
    
    @staticmethod
    def get_processor(metodo_pago: str):
        """
        Obtiene el procesador de pago según el método
        
        Args:
            metodo_pago: 'yape', 'paypal' o 'stripe'
        
        Returns:
            Instancia del procesador correspondiente
        """
        processors = {
            'yape': YapePayment,
            'paypal': PayPalPayment,
            'stripe': StripePayment
        }
        
        processor_class = processors.get(metodo_pago.lower())
        if not processor_class:
            raise ValueError(f"Método de pago no soportado: {metodo_pago}")
        
        return processor_class()