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

## Init
```python
# cd app and change host
python3 uvicorn main:app --host X.X.X.X
```
