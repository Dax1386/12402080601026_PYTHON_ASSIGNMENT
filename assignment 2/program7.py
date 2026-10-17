"""Q7: Stream JSONL sensor data into per-device stats (no full-file load).
Temperature is converted from Celsius to Fahrenheit for reported statistics.
"""
import json, math, sys
from collections import defaultdict
from pathlib import Path

def records(path):
    with open(path,encoding="utf-8") as f:
        for line_no,line in enumerate(f,1):
            try:
                item=json.loads(line)
                if not isinstance(item,dict): raise ValueError("record must be an object")
                yield line_no,item,None
            except (json.JSONDecodeError,ValueError) as exc: yield line_no,None,str(exc)
def summarize(path):
    stats=defaultdict(lambda:{"count":0,"min":math.inf,"max":-math.inf,"sum":0.0,"corrupted":0})
    unassigned_corrupt=0
    for line_no,item,error in records(path):
        if error:
            unassigned_corrupt+=1; continue
        device=item.get("device_id")
        try:
            if not isinstance(device,str) or not device.strip(): raise ValueError("missing device_id")
            temp=float(item["temperature_c"]); humidity=float(item["humidity"])
            if not math.isfinite(temp) or not math.isfinite(humidity): raise ValueError("non-finite measurement")
            s=stats[device]; fahrenheit=temp*9/5+32; s["count"]+=1; s["sum"]+=fahrenheit; s["min"]=min(s["min"],fahrenheit); s["max"]=max(s["max"],fahrenheit)
        except (KeyError,TypeError,ValueError):
            if isinstance(device,str) and device.strip(): stats[device]["corrupted"]+=1
            else: unassigned_corrupt+=1
    return stats,unassigned_corrupt
def main():
    try:
        path=input("JSONL file path: ").strip()
        if not Path(path).is_file(): raise ValueError("File does not exist.")
        stats,unassigned=summarize(path)
        for device,s in sorted(stats.items()):
            avg=s["sum"]/s["count"] if s["count"] else 0
            lo=s["min"] if s["count"] else 0; hi=s["max"] if s["count"] else 0
            print(f"{device} count={s['count']} min={lo:.2f} max={hi:.2f} avg={avg:.2f} corrupted={s['corrupted']}")
        if unassigned: print(f"CORRUPTED_UNKNOWN_DEVICE count={unassigned}")
    except (OSError,ValueError) as e: print(f"Error: {e}",file=sys.stderr); raise SystemExit(1)
if __name__=="__main__": main()
