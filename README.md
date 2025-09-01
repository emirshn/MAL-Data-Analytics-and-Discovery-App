# MAL Data Analytics and Discovery App
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/Vue-3-green)](https://vuejs.org/)

All-in-one data analysis and recommendation tool for anime and manga powered by the MyAnimeList (MAL) database.  
The application combines statistics, recommendations, and visualization into a modern, interactive interface.

<img width="1425" height="663" alt="image" src="https://github.com/user-attachments/assets/f9ebc651-458d-4749-84bd-2d346651b3c5" />

---

## Table of Contents

- [Overview](#overview)  
- [Features](#features)
- [Screenshots](#screenshots)  
- [Installation](#installation)  
- [Usage](#usage)  
- [API Endpoints](#api-endpoints)  
- [Future Work](#future-work)  

---

## Overview

This project provides a full-stack solution for anime and manga fans to explore, filter, and discover. It includes:

- **FastAPI backend** serving MAL data and recommendations.  
- **Vue.js frontend** for browsing series, issues, creators, and recommendations.  
- Recommendation system based on **genres, themes, synopsis and much more**.  

This project uses a MAL dataset that I fetched myself from MAL API and Jikan API you can access actual dataset from backend folder which is zipped for storage limits.
You can test project [here](https://maldiscovery.netlify.app). (I'm using free service so it can be slow)

---

## Features

- **Advanced Search:** Filter and sort anime/manga by genre, score, popularity, and more.
- **Detail Pages:** Dive into in-depth information for specific anime or manga.
- **Comprehensive Data Analysis:** Explore trends, ratings, and statistics for anime and manga.
- **Visualization Tools:** Interactive charts, graphs, and topology-based relationship maps. 
- **Personalized Recommendations:** Get suggestions based on your favorite titles.
- **Efficient Data Handling:**
  - Pre-computed embeddings and metadata allow fast, scalable recommendations.
  - Works with large datasets of thousands of issues without slowing down the API.
- **Web Interface:** Fast and responsive frontend built with Vue 3, compatible with modern browsers

---
## Screenshots
<img width="1301" height="786" alt="image" src="https://github.com/user-attachments/assets/f8299b0e-417c-4224-a821-a477b62d318c" />
<img width="1124" height="702" alt="image" src="https://github.com/user-attachments/assets/83db690f-ccf5-4dc8-a829-ff6170b66848" />
<img width="1043" height="673" alt="image" src="https://github.com/user-attachments/assets/f3480a5f-788f-42ec-821d-cf255cc0574c" />
<img width="1023" height="479" alt="image" src="https://github.com/user-attachments/assets/ecc10707-908a-4ff1-a747-386208e7d08f" />
<img width="1138" height="730" alt="image" src="https://github.com/user-attachments/assets/5d05d0c6-53f2-4fbf-8be5-4d2283f59e4c" />
<img width="1557" height="717" alt="image" src="https://github.com/user-attachments/assets/f9b26e1f-a517-44c9-b44f-8558f996286c" />
<img width="1573" height="737" alt="image" src="https://github.com/user-attachments/assets/28618847-fed8-451a-9b52-d6be4cd5fd4e" />
<img width="1548" height="580" alt="image" src="https://github.com/user-attachments/assets/495cbdcb-9e55-4e84-b0bc-be096d8659e8" />
<img width="1010" height="794" alt="image" src="https://github.com/user-attachments/assets/9e0ea948-e0a9-4375-83c6-348bf41d7ad9" />
<img width="987" height="734" alt="image" src="https://github.com/user-attachments/assets/7d0ff579-e047-49d9-9a2f-95eae29df433" />

---
## Tech Stack

- **Backend**: Python, FastAPI, Pandas, NumPy, Sentence Transformers, Scikit-learn  
- **Frontend**: Vue 3, Vue Router, State Management with Pinia, Tailwind
---


## Installation
1. Backend:
- Clone the repository:
    ```bash
    git clone https://github.com/yourusername/MAL-Data-Analytics-and-Discovery-App.git
    ```
- Navigate to the project directory:
    ```bash
    cd MAL-Data-Analytics-and-Discovery-App
    ```
- Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2. Frontend
- Install libraries:
   ```bash
    npm install
    ```
   
3. Model

   The backend includes `trainanime.py`, which generates the files needed for the recommendation system.
   You can either:
    - Use the pre-trained files included in the repo called `anime_recommender_advanced.pkl.gz`, or
    - Input your own dataset and train embeddings.
   
## Usage

1. Start the backend:
    ```bash
    uvicorn backend.main:app --reload
    ```
2. Start the frontend:
     ```bash
    cd frontend
    npm run dev
    ```
     
3. Open your browser and go to `http://localhost:5000`.

---
## API Endpoints

1. GET /anime/ — list animes from csv file with paging
2. GET /anime/filters - list filters generated from anime csv file like genres, years etc.
3. GET /anime/anime_id - get a detailed information json for given anime id
4. GET /anime/anime_id/image - get a image list for given anime (Used for getting images of relations array for animes which doesnt include image)
5. GET /manga/ — list manga from csv file with paging
6. GET /manga/filters - list filters generated from manga csv file like genres, years etc.
7. GET /manga/manga_id - get a detailed information json for given manga id
8. GET /manga/manga_id/image - get a image list for given manga (Used for getting images of relations array for manga which doesnt include image)
9. GET /graph - returns a nodes and links json generated from relation column
10. GET /stats - get detailed stats in one endpoint
11. GET /anime/search - return a list of possible animes for given input text
12. GET /anime/anime_id/recommend - return a list of recommend animes for given anime
13. GET /anime/multi-recommend - return a list of recommend animes for given multiple animes

---

## Future Work
- Add recommendation for manga too. Right now its only for anime.
- Include characters, peoples etc.
- Enhance statistics dashboards and visualizations.
- Improve recommendation performance and scalability.

---


