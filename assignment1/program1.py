import sys
from collections import defaultdict

def main():
    try:
        input_data = sys.stdin.read().split()
        if not input_data:
            return
        
        n, k, m = int(input_data[0]), int(input_data[1]), int(input_data[2])
        idx = 3
        
        students_by_sem = defaultdict(list)
        subject_toppers = {f"S{j+1}": (-1, []) for j in range(m)} # subject -> (max_mark, list of enrollments)
        
        for _ in range(n):
            enrollment = input_data[idx]
            name = input_data[idx+1]
            sem = int(input_data[idx+2])
            cpi = float(input_data[idx+3])
            marks = [int(input_data[idx+4+j]) for j in range(m)]
            idx += 4 + m
            
            avg_marks = sum(marks) / m
            students_by_sem[sem].append((cpi, avg_marks, enrollment))
            
            # Subject toppers track
            for j, mark in enumerate(marks):
                subj = f"S{j+1}"
                max_mark, toppers = subject_toppers[subj]
                if mark > max_mark:
                    subject_toppers[subj] = (mark, [enrollment])
                elif mark == max_mark:
                    toppers.append(enrollment)
        
        # Output Semester Top K
        for sem in sorted(students_by_sem.keys()):
            # Sort order: CPI desc, Avg Marks desc, Enrollment asc
            students_by_sem[sem].sort(key=lambda x: (-x[0], -x[1], x[2]))
            top_k = [student[2] for student in students_by_sem[sem][:k]]
            print(f"Semester {sem}: {' '.join(top_k)}")
            
        # Output Subject Toppers
        for j in range(m):
            subj = f"S{j+1}"
            _, toppers = subject_toppers[subj]
            toppers.sort()
            print(f"{subj}: {' '.join(toppers)}")

    except Exception as e:
        print(f"Error processing input: {e}")

if __name__ == "__main__":
    main()