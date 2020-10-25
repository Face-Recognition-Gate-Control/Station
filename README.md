# Station

Face Recognition Access Control Application
## Installation

```bash
# python3.6 ++
python -m venv venv

venv/Scripts/activate
```
Begin with installing a compatible version of OpenCV & Torch, then
```python
pip install -r requirements.txt
```


### TODO
- Create a single main.py combining main_vision.py and main_web.py
 
### Testing
#### Test WebApp
```python
uvicorn main_web:app  #(if autoreload use, --reload)
```
#### Test FaceDetector/FaceEmbedder

```python
python main_vision.py
# or single isolated testing use
python main_vision_test.py
```
