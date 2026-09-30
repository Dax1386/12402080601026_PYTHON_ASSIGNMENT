import heapq

def simulate_scheduler(w, jobs):
    # Sort initial arrival
    jobs.sort(key=lambda x: x['arrival'])
    
    ready_queue = [] # Heap storing (-priority, arrival, job_id, duration)
    workers = [0] * w # Free time for each worker
    
    current_time = 0
    job_idx = 0
    total_wait_time = 0
    
    # Store execution records
    completed = []

    while job_idx < len(jobs) or ready_queue:
        # Advance time to earliest available event
        if not ready_queue and current_time < jobs[job_idx]['arrival']:
            current_time = jobs[job_idx]['arrival']

        # Push arrived jobs into ready priority queue
        while job_idx < len(jobs) and jobs[job_idx]['arrival'] <= current_time:
            j = jobs[job_idx]
            heapq.heappush(ready_queue, (-j['priority'], j['arrival'], j['id'], j['duration']))
            job_idx += 1

        # Check available worker
        earliest_worker_id = min(range(w), key=lambda i: workers[i])
        earliest_avail_time = workers[earliest_worker_id]

        if ready_queue:
            prio, arr, jid, dur = heapq.heappop(ready_queue)
            start_time = max(current_time, earliest_avail_time)
            finish_time = start_time + dur
            
            workers[earliest_worker_id] = finish_time
            wait = start_time - arr
            total_wait_time += wait
            
            completed.append((jid, f"W{earliest_worker_id+1}", start_time, finish_time))
            current_time = start_time

    for jid, wid, st, ft in completed:
        print(f"{jid} {wid} {st} {ft}")
    print(f"AVG WAIT {total_wait_time / len(jobs):.2f}")

if __name__ == "__main__":
    jobs_data = [
        {'arrival': 0, 'id': 'J1', 'priority': 2, 'duration': 5, 'resources': 1},
        {'arrival': 1, 'id': 'J2', 'priority': 5, 'duration': 3, 'resources': 1},
        {'arrival': 2, 'id': 'J3', 'priority': 2, 'duration': 2, 'resources': 1}
    ]
    simulate_scheduler(2, jobs_data)