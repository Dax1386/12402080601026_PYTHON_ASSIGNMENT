"""Q9: Inventory model with merge operator. Inventory files are CSV:
product_id,name,stock,purchase_price,selling_price. Commands: ADD/DELETE/UPDATE,
MERGE <file>, COMPARE <file>, SUMMARY. Requires only Python standard library.
"""
import csv, sys
from dataclasses import dataclass
from pathlib import Path
@dataclass
class Product:
    product_id:str; name:str; stock:int; purchase:float; selling:float
    @property
    def value(self): return self.stock*self.purchase
class Inventory:
    def __init__(self,products=None): self.products={p.product_id:p for p in (products or [])}
    @classmethod
    def from_csv(cls,path):
        items=[]
        with open(path,newline="",encoding="utf-8-sig") as f:
            for line,row in enumerate(csv.reader(f),1):
                if not row or row[0].lstrip().startswith("#"): continue
                if line==1 and row[0].lower() in ("product_id","id"): continue
                if len(row)!=5: raise ValueError(f"{path}:{line}: expected 5 columns")
                pid,name,stock,purchase,selling=row; stock=int(stock); purchase=float(purchase); selling=float(selling)
                if stock<0 or purchase<0 or selling<0: raise ValueError(f"{path}:{line}: stock/prices cannot be negative")
                items.append(Product(pid.strip(),name.strip(),stock,purchase,selling))
        return cls(items)
    def __add__(self,other):
        merged={k:Product(v.product_id,v.name,v.stock,v.purchase,v.selling) for k,v in self.products.items()}
        for pid,p in other.products.items():
            if pid in merged:
                old=merged[pid]; old.stock+=p.stock; old.purchase=min(old.purchase,p.purchase); old.selling=max(old.selling,p.selling)
            else: merged[pid]=Product(p.product_id,p.name,p.stock,p.purchase,p.selling)
        return Inventory(merged.values())
    def total_value(self): return sum(p.value for p in self.products.values())
    def show(self):
        for p in sorted(self.products.values(),key=lambda x:x.product_id): print(f"{p.product_id} {p.name} stock={p.stock} purchase={p.purchase:g} selling={p.selling:g}")
        print(f"TOTAL_PURCHASE_VALUE {self.total_value():g}")
def main():
    try:
        inv=Inventory.from_csv(input("Inventory CSV path: ").strip())
        print("Commands: ADD id name stock purchase selling | DELETE id | UPDATE id stock | MERGE file | COMPARE file | SUMMARY | QUIT")
        while True:
            parts=input("> ").strip().split()
            if not parts: continue
            cmd=parts[0].upper()
            if cmd=="QUIT": break
            elif cmd=="ADD" and len(parts)==6:
                pid,name,stock,purchase,selling=parts[1:];
                if pid in inv.products: raise ValueError("Product ID already exists")
                inv.products[pid]=Product(pid,name,int(stock),float(purchase),float(selling)); print("OK")
            elif cmd=="DELETE" and len(parts)==2: print("OK" if inv.products.pop(parts[1],None) else "NOT_FOUND")
            elif cmd=="UPDATE" and len(parts)==3:
                if parts[1] not in inv.products: print("NOT_FOUND")
                else: inv.products[parts[1]].stock=int(parts[2]); print("OK")
            elif cmd=="MERGE" and len(parts)==2:
                inv=inv+Inventory.from_csv(parts[1]); inv.show()
            elif cmd=="COMPARE" and len(parts)==2:
                other=Inventory.from_csv(parts[1]); print("EQUAL" if inv.total_value()==other.total_value() else "GREATER" if inv.total_value()>other.total_value() else "LESS")
            elif cmd=="SUMMARY" and len(parts)==1: inv.show()
            else: print("Invalid command or arguments")
    except (OSError,ValueError) as e: print(f"Error: {e}",file=sys.stderr); raise SystemExit(1)
if __name__=="__main__": main()
