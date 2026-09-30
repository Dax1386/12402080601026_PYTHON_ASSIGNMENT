import csv
from collections import defaultdict
import datetime

def process_transactions(file_path):
    balances = defaultdict(int)
    
    with open(file_path, mode='r', newline='', encoding='utf-8') as infile, \
         open('credit.csv', mode='w', newline='', encoding='utf-8') as credfile, \
         open('debit.csv', mode='w', newline='', encoding='utf-8') as debfile, \
         open('error.csv', mode='w', newline='', encoding='utf-8') as errfile:
        
        reader = csv.reader(infile)
        cred_writer = csv.writer(credfile)
        deb_writer = csv.writer(debfile)
        err_writer = csv.writer(errfile)
        
        # Process Header
        header = next(reader, None)
        if header:
            cred_writer.writerow(header)
            deb_writer.writerow(header)
            err_writer.writerow(header + ['reason'])
            
        for row in reader:
            if not row or len(row) < 5:
                err_writer.writerow(row + ["Insufficient columns"])
                continue
                
            tid, acc, ttype, amount_str, timestamp = [x.strip() for x in row[:5]]
            
            try:
                # Validation rules
                amount = float(amount_str)
                if amount <= 0:
                    raise ValueError("Amount must be positive")
                if ttype not in ("CREDIT", "DEBIT"):
                    raise ValueError("Invalid transaction type")
                datetime.datetime.fromisoformat(timestamp)
                
                # Logic processing
                if ttype == "CREDIT":
                    balances[acc] += amount
                    cred_writer.writerow(row)
                else:
                    balances[acc] -= amount
                    deb_writer.writerow(row)
                    
            except Exception as e:
                err_writer.writerow(row + [str(e)])
                
    # Sort accounts by absolute balance change descending
    sorted_balances = sorted(balances.items(), key=lambda x: abs(x[1]), reverse=True)
    
    for acc, net in sorted_balances:
        print(f"{acc} {int(net) if net.is_integer() else net}")

# Test harness
if __name__ == "__main__":
    sample_data = """tid, acc, type, amount,time
T1,A1, CREDIT,500,2026-01-01T10:00:00
T2, A1, DEBIT, abc, 2026-01-01T10:05:00
T3,A2,DEBIT, 100,2026-01-01T10:10:00"""
    
    with open("transactions.csv", "w") as f:
        f.write(sample_data)
        
    process_transactions("transactions.csv")