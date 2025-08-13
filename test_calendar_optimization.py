#!/usr/bin/env python3
"""
Performance comparison test for calendar color optimization
This script demonstrates the benefits of moving color logic from Python to JavaScript
"""

import time
import json

# Simulate appointment data
appointments = [
    {'id': i, 'status': 'approved', 'is_past': False} for i in range(1, 101)
] + [
    {'id': i, 'status': 'pending', 'is_past': False} for i in range(101, 151)
] + [
    {'id': i, 'status': 'completed', 'is_past': True} for i in range(151, 201)
]

def python_color_processing(appointments):
    """Original server-side color processing"""
    events = []
    
    for appointment in appointments:
        # Original Python color logic
        if appointment['status'] == 'approved':
            bg_color = '#28a745'
            border_color = '#28a745'
        elif appointment['status'] == 'pending':
            bg_color = '#ffc107'
            border_color = '#ffc107'
        elif appointment['status'] == 'completed':
            bg_color = '#6c757d'
            border_color = '#6c757d'
        else:
            bg_color = '#dc3545'
            border_color = '#dc3545'
        
        # Apply transparency for past appointments
        if appointment['is_past']:
            if appointment['status'] == 'approved':
                bg_color = '#28a74580'
                border_color = '#28a74580'
            elif appointment['status'] == 'pending':
                bg_color = '#ffc10780'
                border_color = '#ffc10780'
            elif appointment['status'] == 'completed':
                bg_color = '#6c757d80'
                border_color = '#6c757d80'
        
        events.append({
            'id': appointment['id'],
            'backgroundColor': bg_color,
            'borderColor': border_color,
            'extendedProps': {
                'status': appointment['status'],
                'is_past': appointment['is_past']
            }
        })
    
    return events

def optimized_raw_processing(appointments):
    """Optimized server-side: just send raw data"""
    events = []
    
    for appointment in appointments:
        events.append({
            'id': appointment['id'],
            'extendedProps': {
                'status': appointment['status'],
                'is_past': appointment['is_past']
            }
        })
    
    return events

def test_performance():
    """Test performance comparison"""
    print("🎨 Calendar Color Optimization Performance Test")
    print("=" * 50)
    
    # Test Python color processing multiple times for accuracy
    print("📊 Testing Python color processing...")
    python_times = []
    for _ in range(100):  # Run 100 times for better measurement
        start_time = time.perf_counter()
        python_result = python_color_processing(appointments)
        python_times.append(time.perf_counter() - start_time)
    python_time = sum(python_times) / len(python_times)
    
    # Test optimized raw processing
    print("⚡ Testing optimized raw processing...")
    optimized_times = []
    for _ in range(100):  # Run 100 times for better measurement
        start_time = time.perf_counter()
        optimized_result = optimized_raw_processing(appointments)
        optimized_times.append(time.perf_counter() - start_time)
    optimized_time = sum(optimized_times) / len(optimized_times)
    
    # Results
    print(f"\n📈 RESULTS:")
    print(f"  Python processing: {python_time*1000:.2f} ms (average)")
    print(f"  Optimized processing: {optimized_time*1000:.2f} ms (average)")
    
    if python_time > 0:
        improvement = ((python_time - optimized_time) / python_time * 100)
        print(f"  Performance improvement: {improvement:.1f}%")
    
    # Data size comparison
    python_json = json.dumps(python_result)
    optimized_json = json.dumps(optimized_result)
    
    print(f"\n📦 DATA SIZE:")
    print(f"  Python JSON: {len(python_json):,} bytes")
    print(f"  Optimized JSON: {len(optimized_json):,} bytes")
    size_reduction = ((len(python_json) - len(optimized_json)) / len(python_json) * 100)
    print(f"  Size reduction: {size_reduction:.1f}%")
    
    print(f"\n🚀 BENEFITS:")
    print(f"  ✅ Faster server response times")
    print(f"  ✅ Reduced data transfer")
    print(f"  ✅ Lower server CPU usage")
    print(f"  ✅ Better client-side caching")
    print(f"  ✅ Instant color updates without server round-trips")

if __name__ == "__main__":
    test_performance()
