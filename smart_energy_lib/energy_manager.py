class EnergyAccount:
    def __init__(self, account_id, name, generated=0.0, consumed=0.0, credits=0.0):
        self.account_id = account_id
        self.name = name
        self.generated = float(generated)
        self.consumed = float(consumed)
        self.credits = float(credits)
    
    def calculate_surplus(self):
        return max(0, self.generated - self.consumed)
    
    def calculate_deficit(self):
        return max(0, self.consumed - self.generated)
    
    def calculate_efficiency(self):
        if self.consumed == 0:
            return 100.0
        return (self.generated / self.consumed) * 100
    
    def calculate_self_sufficiency(self):
        if self.consumed == 0:
            return 100.0
        return min(100, (self.generated / self.consumed) * 100)
    
    def calculate_carbon_offset(self, carbon_factor=0.5):
        return self.generated * carbon_factor
    
    def update_energy(self, generated=None, consumed=None):
        if generated is not None:
            self.generated = float(generated)
        if consumed is not None:
            self.consumed = float(consumed)
    
    def add_credits(self, amount):
        self.credits += float(amount)
    
    def deduct_credits(self, amount):
        if self.credits >= amount:
            self.credits -= float(amount)
            return True
        return False
    
    def get_metrics(self):
        return {
            'account_id': self.account_id,
            'name': self.name,
            'generated': self.generated,
            'consumed': self.consumed,
            'credits': self.credits,
            'surplus': self.calculate_surplus(),
            'deficit': self.calculate_deficit(),
            'efficiency': self.calculate_efficiency(),
            'self_sufficiency': self.calculate_self_sufficiency(),
            'carbon_offset': self.calculate_carbon_offset()
        }

class EnergyTransaction:
    TRANSACTION_TYPES = ['buyback', 'loan', 'donation', 'purchase', 'transfer']
    
    def __init__(self, from_account, to_account, amount, transaction_type, rate=0.0):
        if transaction_type not in self.TRANSACTION_TYPES:
            raise ValueError(f"Invalid transaction type")
        
        self.from_account = from_account
        self.to_account = to_account
        self.amount = float(amount)
        self.transaction_type = transaction_type
        self.rate = float(rate)
        self.credits_transferred = self.amount * self.rate
    
    def execute(self):
        if self.from_account.calculate_surplus() < self.amount:
            return False, "Insufficient surplus energy"
        
        self.from_account.consumed += self.amount
        self.from_account.add_credits(self.credits_transferred)
        
        if self.to_account:
            self.to_account.generated += self.amount
        
        return True, "Transaction successful"

class EnergyMarketplace:
    def __init__(self):
        self.accounts = {}
        self.transactions = []
        self.rates = {
            'buyback': 0.15,
            'loan': 0.10,
            'purchase': 0.20,
            'transfer': 0.05
        }
    
    def register_account(self, account):
        self.accounts[account.account_id] = account
    
    def get_account(self, account_id):
        return self.accounts.get(account_id)
    
    def set_rate(self, transaction_type, rate):
        self.rates[transaction_type] = float(rate)
    
    def get_rate(self, transaction_type):
        return self.rates.get(transaction_type, 0.0)

class EnergyCalculator:
    @staticmethod
    def kwh_to_mwh(kwh):
        return kwh / 1000
    
    @staticmethod
    def mwh_to_kwh(mwh):
        return mwh * 1000
    
    @staticmethod
    def calculate_cost(kwh, rate_per_kwh):
        return kwh * rate_per_kwh
    
    @staticmethod
    def calculate_savings(generated, consumed, grid_rate):
        self_consumed = min(generated, consumed)
        return self_consumed * grid_rate
    
    @staticmethod
    def estimate_solar_generation(panel_capacity_kw, hours_sun, efficiency=0.85):
        return panel_capacity_kw * hours_sun * efficiency
