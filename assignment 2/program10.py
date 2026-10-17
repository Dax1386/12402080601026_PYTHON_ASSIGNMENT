"""
Q10: Clean student marks CSV, export summary and three charts.
Requires: pip install matplotlib. CSV columns: enrollment,name,subject marks...
Missing marks are imputed with that subject's median; no numeric values => 0.
Grades: A >=90, B >=80, C >=70, D >=60, F <60. Top performer = highest mean.
"""
import csv, math, sys
from pathlib import Path
import matplotlib.pyplot as plt

def median(values):
    vals=sorted(values)
    if not vals:return 0.0
    n=len(vals); return vals[n//2] if n%2 else (vals[n//2-1]+vals[n//2])/2

def run(input_path,output_path):
    out=Path(output_path); out.mkdir(parents=True,exist_ok=True)
    with open(input_path,newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        if not reader.fieldnames or not {"enrollment","name"}.issubset(reader.fieldnames): raise ValueError("CSV needs enrollment and name columns")
        subjects=[c for c in reader.fieldnames if c not in ("enrollment","name")]
        if not subjects or len(subjects)>20: raise ValueError("Provide between 1 and 20 subject columns")
        students=[]
        for line,row in enumerate(reader,2):
            marks={}
            for sub in subjects:
                raw=(row.get(sub) or "").strip()
                try:
                    v=float(raw) if raw else None
                    if v is not None and (not math.isfinite(v) or not 0<=v<=100): raise ValueError()
                except ValueError: raise ValueError(f"Invalid mark at row {line}, subject {sub}")
                marks[sub]=v
            students.append({"enrollment":row["enrollment"],"name":row["name"],"marks":marks})
    fills={s:median([x["marks"][s] for x in students if x["marks"][s] is not None]) for s in subjects}
    for x in students:
        for s in subjects:
            if x["marks"][s] is None:x["marks"][s]=fills[s]
        x["average"]=sum(x["marks"].values())/len(subjects)
    with open(out/"cleaned_marks.csv","w",newline="",encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["enrollment","name",*subjects]);
        for x in students:w.writerow([x["enrollment"],x["name"],*[f"{x['marks'][s]:g}" for s in subjects]])
    with open(out/"summary.csv","w",newline="",encoding="utf-8") as f:
        w=csv.writer(f);w.writerow(["subject","count","average","minimum","maximum"])
        for s in subjects:
            vals=[x["marks"][s] for x in students];w.writerow([s,len(vals),f"{sum(vals)/len(vals):.2f}" if vals else "0.00",f"{min(vals):g}" if vals else "0",f"{max(vals):g}" if vals else "0"])
    buckets={g:0 for g in "ABCDF"}
    for x in students:
        for score in x["marks"].values(): buckets["A" if score>=90 else "B" if score>=80 else "C" if score>=70 else "D" if score>=60 else "F"]+=1
    plt.figure(figsize=(7,4));plt.bar(buckets.keys(),buckets.values(),color="#4472c4");plt.title("Grade Distribution");plt.xlabel("Grade");plt.ylabel("Number of subject marks");plt.tight_layout();plt.savefig(out/"grade_distribution.png",dpi=160);plt.close()
    avgs=[sum(x["marks"][s] for x in students)/len(students) if students else 0 for s in subjects]
    plt.figure(figsize=(max(7,len(subjects)*.7),4));plt.bar(subjects,avgs,color="#70ad47");plt.title("Subject-wise Average");plt.ylabel("Average mark");plt.ylim(0,100);plt.xticks(rotation=30,ha="right");plt.tight_layout();plt.savefig(out/"subject_average.png",dpi=160);plt.close()
    top=sorted(students,key=lambda x:(-x["average"],x["enrollment"]))[:10]
    plt.figure(figsize=(8,4));plt.bar([x["name"] for x in top],[x["average"] for x in top],color="#ed7d31");plt.title("Top Performers (by mean mark)");plt.ylabel("Average mark");plt.ylim(0,100);plt.xticks(rotation=30,ha="right");plt.tight_layout();plt.savefig(out/"top_performers.png",dpi=160);plt.close()
    print("Created cleaned_marks.csv, summary.csv, and three chart images in",out)
def main():
    try: run(input("Marks CSV path: ").strip(),input("Output folder: ").strip())
    except (OSError,ValueError) as e: print(f"Error: {e}",file=sys.stderr);raise SystemExit(1)
if __name__=="__main__":main()
