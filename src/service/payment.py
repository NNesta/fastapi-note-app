

class Payment():

    def __init__(self, payment_option):
        self.payment_option = payment_option
    
    def pay(self):
        return self.payment_option.pay()


class StripePayment:
    def pay(self):
        print("Paid using stripe")

class PaypalPayment:
    def pay(self):
        print("Paid using paypal")

payment = Payment(StripePayment())

