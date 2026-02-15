# <p align="center">Finger-Mouse</p>
Base on Google's MediaPipe and OpenCV,support multiple gesture controls for mouse operation.
## Usage
You can use this project to control your mouse with your fingers.The project is used camera input,so you can far away your computer.

### System architecture design
#### 1. Modular Design
- **Detection Layer**: Responsible for detecting and tracking hand key points
- **Recognition Layer**: Handles the extraction and classification of gesture features
- **Control Layer**: Executes mouse simulation and system control
- **Interface Layer**: Provides user interaction and parameter adjustment
#### 2. Data flow
```
Camera input → Image preprocessing → Key point detection → Feature extraction → Gesture recognition → Mouse control → Interface feedback
```

## Project structure

```
FingerMouse/
├── main.py                 # Program entry point
├── requirements.txt        # Dependency package list
├── README.md              # Project Description Document
├── config/                
│   ├── __init__.py
│   ├── settings.py        
│   └── config_manager.py
├── gui/                   
│   ├── __init__.py
│   ├── main_window.py     
│   ├── controls_panel.py  
│   └── preview_panel.py   
├── recognition/           
│   ├── __init__.py
│   ├── hand_detector.py   
│   ├── gesture_recognizer.py 
│   └── gesture_processor.py 
├── control/       
│   ├── __init__.py
│   ├── mouse_controller.py
│   └── keyboard_listener.py
├── utils/                
    ├── __init__.py
    ├── logger.py        
    ├── camera_manager.py
    └── camera_scanner.py
```

## Running

### 1. Environment Setup

```bash
conda create -n finger-mouse python=3.8
conda activate finger-mouse
pip install -r requirements.txt
```

### 2. Run Project

```bash
python main.py
```

### 3. How to use

1. Click "Start Recognition" to start gesture recognition.
2. Click "Enable Mouse Control" to activate mouse simulation.
3. Use different gestures to control mouse operations:
- **Touch the thumb and index finger together**: Left mouse button
- **Touch the thumb and middle finger together**: Right mouse button
- **Touch the bottom of the thumb and index finger together**: Scroll up
- **Touch the thumb on the base of the index finger**: Scroll down

## Contribution Guidelines 
Welcome to submit Issues and Pull Requests to improve the project!


## Thanks

- [MediaPipe](https://github.com/google/mediapipe)
- [OpenCV](https://opencv.org/)
- [pynput](https://pynput.readthedocs.io/)

## Core algorithm

### Dynamic threshold adjustment algorithm
```python
def adaptive_threshold_adjustment(current_value, baseline_threshold, adaptation_rate=0.05):
    # Calculate the offset
    offset = current_value - baseline_threshold
    
    adjusted_threshold = baseline_threshold + offset * adaptation_rate
    
    # Limit the maximum adjustment
    max_adjustment = baseline_threshold * 0.3  # Max adjustment 30%
    adjusted_threshold = max(
        baseline_threshold - max_adjustment,
        min(baseline_threshold + max_adjustment, adjusted_threshold)
    )
    
    return adjusted_threshold
```
### Multi-frame voting mechanism
```python
def multi_frame_voting(gesture_history, voting_window=8):
    if len(gesture_history) < voting_window:
        return gesture_history[-1] if gesture_history else None
    
    # Count the frequency of each gesture's appearance
    vote_count = {}
    recent_gestures = gesture_history[-voting_window:]
    
    for gesture in recent_gestures:
        vote_count[gesture] = vote_count.get(gesture, 0) + 1
    
    most_voted_gesture = max(vote_count.items(), key=lambda x: x[1])[0]
    
    # Limit the maximum uncertainty
    min_votes_required = voting_window * 0.6
    if vote_count[most_voted_gesture] >= min_votes_required:
        return most_voted_gesture
    else:
        return None
```

### Mouse control

#### 1. Coordinate mapping
- **Normalization**：Let the standardized coordinates (-1,1) of MediaPipe are converted to pixel coordinates.
- **Screen Adapter**：Adaptive mapping supporting screens of different resolutions
- **Boundary Treatment**：Prevent the mouse from going beyond the screen boundaries
- **Y-axis Inversion**：Correct the differences between the camera coordinate system and the screen coordinate system

#### 2. Motion smoothing algorithm
- **Exponential Moving Average**: Utilizes the EMA algorithm to smooth the mouse movement trajectory
- **Predictive Interpolation**: Predicts the next position based on historical movement trends
- **Acceleration Compensation**: Dynamically adjusts the mouse sensitivity according to the speed of hand movement
- **Dead Zone Filtering**: Ignores minor hand tremors to improve control accuracy

#### 3. Anti-Auto-Fire Control Mechanism  
- **Cooldown Management**: Sets independent cooldown periods for each gesture.
- **State Locking Mechanism**: Prevents repeated triggering of the same gesture.
- **Gesture Change Detection**: Executes actions only upon detection of a valid state change.
- **Multi-Layer Protection**: Combines timestamp and state flagging for dual protection.
#### 4. High Frame Rate Optimization
- **Frame Rate Adaptation**: Dynamically adjusts the processing frame rate based on system performance.
- **Batch Processing Optimization**: Employs batch processing at high frame rates to reduce system calls.
- **Caching Mechanism**: Caches recent computation results to avoid redundant calculations.
- **Asynchronous Updates**: Uses asynchronous methods to update the GUI for maintaining smoothness.

### FPS Optimization
```python
def calculate_optimal_fps(process_time_ms, safety_margin=0.8):
    if process_time_ms <= 0:
        return 30
    
    theoretical_max_fps = 1000.0 / process_time_ms
    optimal_fps = int(theoretical_max_fps * safety_margin)
    
    return max(15, min(120, optimal_fps))
```
### Cache hit rate
```python
def cache_performance_model(cache_size, access_pattern_skewness=0.8):
    hit_rate = 1.0 - (1.0 / (cache_size ** access_pattern_skewness))
    return hit_rate
```

### Delayed Statistics
```python
class LatencyMonitor:
    def __init__(self, window_size=100):
        self.latencies = deque(maxlen=window_size)
        self.timestamps = deque(maxlen=window_size)
    
    def add_measurement(self, latency_ms):
        self.latencies.append(latency_ms)
        self.timestamps.append(time.time())
    
    def get_statistics(self):
        if not self.latencies:
            return None
        latencies_list = list(self.latencies)
        stats = {
            'mean': sum(latencies_list) / len(latencies_list),
            'median': sorted(latencies_list)[len(latencies_list)//2],
            'min': min(latencies_list),
            'max': max(latencies_list),
            'std_dev': (sum((x - sum(latencies_list)/len(latencies_list))**2 
                          for x in latencies_list) / len(latencies_list))**0.5,
            'percentile_95': sorted(latencies_list)[int(len(latencies_list) * 0.95)],
            'percentile_99': sorted(latencies_list)[int(len(latencies_list) * 0.99)]
        }
        
        return stats
```
### Shaking
```python
def calculate_jitter(latency_measurements):
    if len(latency_measurements) < 2:
        return 0
    
    differences = [abs(latency_measurements[i] - latency_measurements[i-1]) 
                   for i in range(1, len(latency_measurements))]
    
    jitter = (sum(d**2 for d in differences) / len(differences))**0.5
    return jitter

def predict_response_time(current_load, baseline_time, load_coefficient=1.2):
    predicted_time = baseline_time * (current_load ** load_coefficient)
    return predicted_time
```

### Coordinate transformation algorithm

#### 1. Normalization
Make MediaPipe coordinate range[-1,1] to screen pixel coordinates[0, width]×[0,height]
```python
screen_x = int((landmark_x + 1) * screen_width / 2)
screen_y = int((-landmark_y + 1) * screen_height / 2) 
```
$$ x_{pixel} = (x_{normalized} + 1) × width/2 $$
$$ y_{pixel} = (1 - y_{normalized}) × height/2 $$

#### 2. Perspective transformation matrix
```python
def calculate_perspective_transform(src_points, dst_points):
    """
    src_points: Source plane [(x1,y1), (x2,y2), (x3,y3), (x4,y4)]
    dst_points: Target plane [(x1',y1'), (x2',y2'), (x3',y3'), (x4',y4')]
    """
    matrix = cv2.getPerspectiveTransform(
        np.float32(src_points), 
        np.float32(dst_points)
    )
    return matrix
transformed_coords = cv2.perspectiveTransform(
    np.array([[[landmark_x, landmark_y]]]), 
    perspective_matrix
)[0][0]
```
#### 3. Smooth control algorithm
```python
smoothed_x = last_smoothed_x * smoothing_factor + current_x * (1 - smoothing_factor)
smoothed_y = last_smoothed_y * smoothing_factor + current_y * (1 - smoothing_factor)
```
$$ S_t = α × S_{t-1} + (1-α) × X_t $$


**α = smoothing_factor, S_t is smooth the post-coordinates, X_t is the current coordinates**

### Predictive smoothing
```python
predicted_x = 2 * smoothed_x - last_smoothed_x + acceleration_x * prediction_factor
predicted_y = 2 * smoothed_y - last_smoothed_y + acceleration_y * prediction_factor
```
### Acceleration calculation
```python
acceleration_x = (smoothed_x - last_smoothed_x) - (last_smoothed_x - prev_smoothed_x)
acceleration_y = (smoothed_y - last_smoothed_y) - (last_smoothed_y - prev_smoothed_y)
```

### 5. Distance check

**Euclidean distance calculation**
```python
def calculate_euclidean_distance(point1, point2):
    dx = point1[0] - point2[0]
    dy = point1[1] - point2[1]
    dz = point1[2] - point2[2]
    return math.sqrt(dx*dx + dy*dy + dz*dz)
```
$$d = √[(x₂-x₁)² + (y₂-y₁)² + (z₂-z₁)²]$$