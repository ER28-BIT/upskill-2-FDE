"""Generate sample data for testing the MVP."""
import json
import random
from datetime import datetime, timedelta

def generate_sample_events(num_events=100):
    """Generate sample event data."""
    event_types = ['transaction', 'login', 'logout', 'error', 'warning', 'info']
    statuses = ['success', 'failed', 'pending', 'cancelled']
    customers = [f'CUST_{i:04d}' for i in range(1, 21)]
    
    events = []
    base_time = datetime.utcnow() - timedelta(days=30)
    
    for i in range(num_events):
        event_time = base_time + timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        event_type = random.choice(event_types)
        customer_id = random.choice(customers)
        
        # Generate value based on event type
        if event_type == 'transaction':
            value = round(random.uniform(10, 10000), 2)
        else:
            value = None
        
        # Status distribution (more success than failures)
        status = random.choices(
            statuses,
            weights=[70, 15, 10, 5],
            k=1
        )[0]
        
        event = {
            'event_type': event_type,
            'customer_id': customer_id,
            'timestamp': event_time.isoformat(),
            'value': value,
            'status': status,
            'metadata': {
                'source': 'sample_generator',
                'environment': 'test',
                'tags': [event_type, customer_id[:7]]
            }
        }
        events.append(event)
    
    return events

if __name__ == '__main__':
    # Generate sample events
    events = generate_sample_events(200)
    
    # Save to JSON file
    output_file = 'data/raw/sample_events.json'
    with open(output_file, 'w') as f:
        json.dump(events, f, indent=2)
    
    print(f"Generated {len(events)} sample events")
    print(f"Saved to {output_file}")
    
    # Print summary
    event_types = {}
    for event in events:
        event_type = event['event_type']
        event_types[event_type] = event_types.get(event_type, 0) + 1
    
    print("\nEvent type distribution:")
    for event_type, count in sorted(event_types.items()):
        print(f"  {event_type}: {count}")
