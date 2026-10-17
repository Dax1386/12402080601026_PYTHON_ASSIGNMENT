"""Q6: Detect qualifying failed-login sequences followed by another-IP success.
Input: X T, then n, then lines HH:MM user ip FAIL|SUCCESS. Midnight wrap is not modeled.
"""
from collections import defaultdict, deque
from datetime import datetime
import re, sys
LINE_RE=re.compile(r"^(\d{2}:\d{2})\s+(\S+)\s+(\S+)\s+(FAIL|SUCCESS)$")
def minutes(clock):
    t=datetime.strptime(clock,"%H:%M"); return t.hour*60+t.minute
def detect(lines,x,window):
    failures=defaultdict(deque); findings={}
    for line in lines:
        m=LINE_RE.fullmatch(line.strip())
        if not m: raise ValueError(f"Malformed log line: {line.rstrip()}")
        stamp,user,ip,status=m.groups(); now=minutes(stamp); q=failures[user]
        while q and now-q[0][0]>window: q.popleft()
        if status=="FAIL": q.append((now,ip))
        elif len(q)>=x and any(old_ip!=ip for _,old_ip in q): findings.setdefault(user,stamp)
    return findings
def main():
    try:
        x,t=map(int,input("X T: ").split()); n=int(input("Number of logs: "))
        if not 1<=x<=100 or not 1<=t<=1440 or n<0: raise ValueError("X/T/n outside allowed range")
        lines=[input() for _ in range(n)]
        for user,stamp in sorted(detect(lines,x,t).items()): print(user,stamp)
    except (ValueError,OverflowError) as e: print(f"Error: {e}",file=sys.stderr); raise SystemExit(1)
if __name__=="__main__": main()
