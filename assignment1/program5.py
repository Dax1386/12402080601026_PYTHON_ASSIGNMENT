class InsufficientFundsError(Exception): pass
class AccountNotFoundError(Exception): pass
class BatchFailedError(Exception): pass

class Account:
    def __init__(self, acc_id, balance):
        self.acc_id = acc_id
        self._balance = balance

    @property
    def balance(self):
        return self._balance

    def deposit(self, amount):
        self._balance += amount

    def withdraw(self, amount):
        if self._balance < amount:
            raise InsufficientFundsError("Insufficient balance")
        self._balance -= amount

class Bank:
    def __init__(self):
        self.accounts = {}

    def add_account(self, acc_id, balance):
        self.accounts[acc_id] = Account(acc_id, balance)

    def execute_operations(self, operations):
        batch_mode = False
        batch_operations = []
        batch_counter = 0
        
        for op in operations:
            tokens = op.split()
            cmd = tokens[0]

            if cmd == "BATCH_BEGIN":
                batch_mode = True
                batch_operations = []
                batch_counter += 1
            elif cmd == "BATCH_END":
                batch_mode = False
                # Attempt executing entire batch with rollback support
                snapshots = {acc_id: acc.balance for acc_id, acc in self.accounts.items()}
                try:
                    for b_cmd, *b_args in batch_operations:
                        self._apply_op(b_cmd, b_args)
                except Exception:
                    # Rollback
                    for acc_id, bal in snapshots.items():
                        self.accounts[acc_id]._balance = bal
                    print(f"FAILED {batch_counter}")
            else:
                if batch_mode:
                    batch_operations.append((cmd, tokens[1:]))
                else:
                    try:
                        self._apply_op(cmd, tokens[1:])
                    except Exception as e:
                        pass

    def _apply_op(self, cmd, args):
        if cmd == "DEPOSIT":
            acc_id, amt = args[0][0], int(args[0][1])
            if acc_id not in self.accounts: raise AccountNotFoundError()
            self.accounts[acc_id].deposit(amt)
        elif cmd == "WITHDRAW":
            acc_id, amt = args[0][0], int(args[0][1])
            if acc_id not in self.accounts: raise AccountNotFoundError()
            self.accounts[acc_id].withdraw(amt)
        elif cmd == "TRANSFER":
            src, dst, amt = args[0][0], args[0][1], int(args[0][2])
            if src not in self.accounts or dst not in self.accounts: raise AccountNotFoundError()
            self.accounts[src].withdraw(amt)
            self.accounts[dst].deposit(amt)

    def print_balances(self):
        for acc_id in sorted(self.accounts.keys()):
            print(f"{acc_id} {self.accounts[acc_id].balance}")

# Sample Execution
if __name__ == "__main__":
    bank = Bank()
    bank.add_account("A", 1000)
    bank.add_account("B", 200)
    bank.add_account("C", 0)
    
    ops = [
        "TRANSFER A B 300",
        "BATCH_BEGIN",
        "WITHDRAW B 1000",
        "DEPOSIT C 50",
        "BATCH_END"
    ]
    
    bank.execute_operations(ops)
    bank.print_balances()