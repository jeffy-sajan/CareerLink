import razorpay
from django.conf import settings

# Initialize Razorpay client
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def get_subscription_plans(user_type):
    """Get available plans based on user type"""
    plans = {
        'job_seeker': {
            'name': 'Premium Job Seeker',
            'price': 999,  # ₹999
            'type': 'job_seeker',
            'features': [
                'Priority application visibility',
                'Premium badge on profile',
                'Priority consideration by employers'
            ]
        },
        'employer': {
            'name': 'Premium Employer',
            'price': 1999,  # ₹1999
            'type': 'employer',
            'features': [
                'Unlimited job postings',
                'Premium badge on company profile',
                'Advanced analytics'
            ]
        }
    }
    return [plans[user_type]] if user_type in plans else []

def create_subscription(plan_id, user_email, user_name):
    """Create a one-time payment order"""
    # Determine amount based on plan type
    amount = 99900 if 'job_seeker' in plan_id else 199900  # Amount in paise (₹999 or ₹1999)
    
    # Create order
    order_data = {
        'amount': amount,
        'currency': 'INR',
        'notes': {
            'plan_id': plan_id,
            'user_email': user_email,
            'user_name': user_name
        }
    }
    
    try:
        order = client.order.create(data=order_data)
        return order
    except Exception as e:
        print(f"Error creating order: {str(e)}")
        return None

def verify_payment(payment_id, order_id, signature):
    """Verify Razorpay payment signature"""
    try:
        return client.utility.verify_payment_signature({
            'razorpay_payment_id': payment_id,
            'razorpay_order_id': order_id,
            'razorpay_signature': signature
        })
    except Exception as e:
        print(f"Payment verification failed: {str(e)}")
        return False 