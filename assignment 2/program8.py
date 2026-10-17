"""Q8: Maximum-score grid path with right/down/diagonal moves and path count.
Blocked cells are X; memory O(m). Counts are modulo 1,000,000,007.
"""
import sys
MOD=1_000_000_007

def solve(grid):
    n=len(grid); m=len(grid[0]) if n else 0
    # Each column holds (best score ending here, number of ways).
    dp=[None]*m
    for i in range(n):
        diag=None
        for j in range(m):
            old=dp[j]; above=old; left=dp[j-1] if j else None; diagonal=diag
            diag=above
            value=grid[i][j]
            if value is None: dp[j]=None; continue
            if i==0 and j==0: dp[j]=(value,1); continue
            candidates=[x for x in (above,left,diagonal) if x is not None]
            if not candidates: dp[j]=None; continue
            best=max(x[0] for x in candidates)
            ways=sum(x[1] for x in candidates if x[0]==best)%MOD
            dp[j]=(best+value,ways)
    return dp[-1]
def main():
    try:
        n,m=map(int,input().split())
        if not (1<=n<=2000 and 1<=m<=2000): raise ValueError("n and m must be in 1..2000")
        grid=[]
        for _ in range(n):
            row=input().split()
            if len(row)!=m: raise ValueError("Each row must contain exactly m cells")
            grid.append([None if x.upper()=="X" else int(x) for x in row])
        answer=solve(grid)
        print("IMPOSSIBLE" if answer is None else f"{answer[0]} {answer[1]}")
    except ValueError as e: print(f"Error: {e}",file=sys.stderr); raise SystemExit(1)
if __name__=="__main__": main()
