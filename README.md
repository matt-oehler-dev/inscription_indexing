# Inscription Indexing


Deployed at: https://inscription-indexing.onrender.com
- it's pretty slow though and is only set to run on 500 images

To run locally:
- clone this repository and go to its root directory
- (optional) set up and activate a virtual environment
- run: 
    - `pip install -r requirements_app.txt`
- (optional) to run on the full set of images instead of just 500
    - in `image_search.py` on line 10 change it to:
        -  `USE_SAMPLED_SET_OF_IMAGES = False`
- run:
    - `streamlit run image_search.py`