import os
import pandas as pd
import ast
import numpy as np
import pickle
import gzip
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from sklearn.preprocessing import MultiLabelBinarizer, StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import KMeans
import re
from collections import Counter, defaultdict
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RecommendationConfig:
    """Configuration class for recommendation parameters"""
    top_k: int = 10
    min_score: float = 6.5
    include_sequels: bool = False
    diversity_factor: float = 0.1
    explain: bool = True
    use_clustering: bool = True
    cluster_weight: float = 0.2

@dataclass
class AnimeInfo:
    """Data class for anime information"""
    mal_id: int
    title: str
    title_english: str = ""
    score: Optional[float] = None
    type: str = ""
    episodes: Optional[int] = None
    year: Optional[int] = None
    genres: List[str] = None
    themes: List[str] = None
    synopsis: str = ""
    similarity: Optional[float] = None
    explanation: str = ""

class AdvancedAnimeRecommender:
    """
    Advanced Anime Recommendation System with improved features:
    - Better feature engineering with semantic groupings
    - Clustering-based recommendations for diversity
    - Enhanced explanation system
    - Configurable parameters
    - Better error handling and logging
    - Optimized memory usage
    """
    
    def __init__(self, config: Optional[RecommendationConfig] = None):
        self.config = config or RecommendationConfig()
        self.df: Optional[pd.DataFrame] = None
        self.features: Optional[np.ndarray] = None
        self.clusters: Optional[np.ndarray] = None
        self.cluster_model: Optional[KMeans] = None
        self.scaler: Optional[StandardScaler] = None
        self.genre_groups: Dict[str, List[str]] = {}
        self.model_info: Dict[str, Any] = {}
        self.feature_names: List[str] = []
        
        # Cache for frequent operations
        self._similarity_cache: Dict[Tuple[int, int], float] = {}
        self._explanation_cache: Dict[Tuple[int, int], str] = {}
        
    def parse_list(self, x: Any) -> List[str]:
        """Parse JSON-like strings to extract names with better error handling"""
        if pd.isna(x) or x == "":
            return []
        
        try:
            if isinstance(x, str) and x.startswith("["):
                parsed = ast.literal_eval(x)
                if isinstance(parsed, list):
                    return [d.get("name", "") for d in parsed if isinstance(d, dict) and "name" in d]
            elif isinstance(x, list):
                return x
            return []
        except (ValueError, SyntaxError) as e:
            logger.warning(f"Failed to parse list: {x}, error: {e}")
            return []
    
    def setup_enhanced_genre_groups(self) -> None:
        """Enhanced semantic genre groups with cross-genre bridge categories"""
        self.genre_groups = {
            # Core demographics and target audience
            'shounen_action': ['Action', 'Adventure', 'Shounen', 'Super Power', 'Martial Arts', 'Tournament'],
            'seinen_mature': ['Seinen', 'Psychological', 'Thriller', 'Adult Cast', 'Workplace'],
            'shoujo_romance': ['Shoujo', 'Romance', 'School', 'Josei'],
            'josei_adult': ['Josei', 'Romance', 'Drama', 'Adult Cast'],
            
            # Genre combinations
            'dark_psychological': ['Horror', 'Thriller', 'Psychological', 'Gore', 'Supernatural'],
            'comedy_lighthearted': ['Comedy', 'Slice of Life', 'School', 'Gag Humor', 'Parody'],
            'sci_fi_tech': ['Sci-Fi', 'Mecha', 'Space', 'Cyberpunk', 'Technology'],
            'fantasy_magic': ['Fantasy', 'Magic', 'Supernatural', 'Mythology', 'Isekai'],
            
            # Thematic groups
            'sports_competition': ['Sports', 'Team Sports', 'Racing', 'Strategy Game'],
            'music_arts': ['Music', 'Performing Arts', 'Idols (Female)', 'Idols (Male)'],
            'historical_period': ['Historical', 'Samurai', 'Military'],
            'slice_of_life': ['Slice of Life', 'Iyashikei', 'CGDCT'],
            
            # Advanced themes
            'existential_deep': ['Philosophical', 'Psychological', 'Drama', 'Tragedy'],
            'adventure_journey': ['Adventure', 'Survival', 'Travel'],
            'mystery_detective': ['Mystery', 'Detective', 'Police'],
            'war_conflict': ['Military', 'War', 'Combat Sports'],
            
            # SPORTS BRIDGE CATEGORIES
            'psychological_sports': ['Sports', 'Psychological', 'Drama', 'Mental Health'],
            'action_sports': ['Sports', 'Action', 'Tournament', 'Martial Arts'],
            'supernatural_sports': ['Sports', 'Supernatural', 'Super Power', 'Fantasy'],
            'comedy_sports': ['Sports', 'Comedy', 'School', 'Slice of Life'],
            'romance_sports': ['Sports', 'Romance', 'School', 'Drama'],
            'dark_sports': ['Sports', 'Thriller', 'Psychological', 'Tragedy'],
            'team_drama': ['Sports', 'Drama', 'Friendship', 'Coming-of-Age'],
            'competitive_mindset': ['Sports', 'Strategy Game', 'Psychological', 'Mind Games'],
            
            # ACTION BRIDGE CATEGORIES
            'psychological_action': ['Action', 'Psychological', 'Thriller', 'Mind Games'],
            'comedy_action': ['Action', 'Comedy', 'Parody', 'Adventure'],
            'romance_action': ['Action', 'Romance', 'Adventure', 'Drama'],
            'sci_fi_action': ['Action', 'Sci-Fi', 'Mecha', 'Space'],
            'fantasy_action': ['Action', 'Fantasy', 'Magic', 'Supernatural'],
            'historical_action': ['Action', 'Historical', 'Samurai', 'Military'],
            'horror_action': ['Action', 'Horror', 'Supernatural', 'Gore'],
            'school_action': ['Action', 'School', 'Shounen', 'Super Power'],
            
            # PSYCHOLOGICAL BRIDGE CATEGORIES
            'psychological_horror': ['Psychological', 'Horror', 'Thriller', 'Supernatural'],
            'psychological_romance': ['Psychological', 'Romance', 'Drama', 'Adult Cast'],
            'psychological_sci_fi': ['Psychological', 'Sci-Fi', 'Cyberpunk', 'Philosophy'],
            'psychological_fantasy': ['Psychological', 'Fantasy', 'Supernatural', 'Mystery'],
            'psychological_mystery': ['Psychological', 'Mystery', 'Thriller', 'Detective'],
            'psychological_slice_of_life': ['Psychological', 'Slice of Life', 'Drama', 'Adult Cast'],
            'psychological_school': ['Psychological', 'School', 'Drama', 'Coming-of-Age'],
            
            # ROMANCE BRIDGE CATEGORIES
            'dark_romance': ['Romance', 'Psychological', 'Thriller', 'Drama'],
            'action_romance': ['Romance', 'Action', 'Adventure', 'Fantasy'],
            'sci_fi_romance': ['Romance', 'Sci-Fi', 'Space', 'Drama'],
            'fantasy_romance': ['Romance', 'Fantasy', 'Magic', 'Supernatural'],
            'historical_romance': ['Romance', 'Historical', 'Drama', 'Period'],
            'comedy_romance': ['Romance', 'Comedy', 'School', 'Slice of Life'],
            'music_romance': ['Romance', 'Music', 'Drama', 'Performing Arts'],
            'supernatural_romance': ['Romance', 'Supernatural', 'Fantasy', 'Drama'],
            
            # HORROR/THRILLER BRIDGE CATEGORIES
            'action_horror': ['Horror', 'Action', 'Supernatural', 'Gore'],
            'psychological_thriller': ['Thriller', 'Psychological', 'Mystery', 'Suspense'],
            'sci_fi_horror': ['Horror', 'Sci-Fi', 'Thriller', 'Supernatural'],
            'supernatural_thriller': ['Thriller', 'Supernatural', 'Mystery', 'Horror'],
            'school_horror': ['Horror', 'School', 'Supernatural', 'Thriller'],
            
            # COMEDY BRIDGE CATEGORIES
            'action_comedy': ['Comedy', 'Action', 'Adventure', 'Parody'],
            'romantic_comedy': ['Comedy', 'Romance', 'School', 'Slice of Life'],
            'fantasy_comedy': ['Comedy', 'Fantasy', 'Magic', 'Parody'],
            'sci_fi_comedy': ['Comedy', 'Sci-Fi', 'Parody', 'Space'],
            'school_comedy': ['Comedy', 'School', 'Slice of Life', 'Gag Humor'],
            'supernatural_comedy': ['Comedy', 'Supernatural', 'Fantasy', 'Parody'],
            
            # SCI-FI BRIDGE CATEGORIES
            'mecha_action': ['Sci-Fi', 'Mecha', 'Action', 'Military'],
            'cyberpunk_thriller': ['Sci-Fi', 'Cyberpunk', 'Thriller', 'Psychological'],
            'space_adventure': ['Sci-Fi', 'Space', 'Adventure', 'Action'],
            'sci_fi_drama': ['Sci-Fi', 'Drama', 'Psychological', 'Philosophy'],
            'time_travel': ['Sci-Fi', 'Drama', 'Romance', 'Mystery'],
            
            # FANTASY BRIDGE CATEGORIES
            'dark_fantasy': ['Fantasy', 'Horror', 'Supernatural', 'Gore'],
            'adventure_fantasy': ['Fantasy', 'Adventure', 'Action', 'Magic'],
            'isekai_adventure': ['Fantasy', 'Isekai', 'Adventure', 'Comedy'],
            'magical_girl': ['Fantasy', 'Magic', 'Shoujo', 'Action'],
            'mythology_fantasy': ['Fantasy', 'Mythology', 'Historical', 'Supernatural'],
            
            # DRAMA BRIDGE CATEGORIES
            'slice_of_life_drama': ['Drama', 'Slice of Life', 'Adult Cast', 'Workplace'],
            'historical_drama': ['Drama', 'Historical', 'Period', 'Romance'],
            'family_drama': ['Drama', 'Family', 'Slice of Life', 'Coming-of-Age'],
            'music_drama': ['Drama', 'Music', 'Performing Arts', 'Romance'],
            'workplace_drama': ['Drama', 'Workplace', 'Adult Cast', 'Seinen'],
            
            # SCHOOL/YOUTH BRIDGE CATEGORIES
            'school_drama': ['School', 'Drama', 'Coming-of-Age', 'Slice of Life'],
            'school_supernatural': ['School', 'Supernatural', 'Mystery', 'Horror'],
            'school_romance': ['School', 'Romance', 'Comedy', 'Drama'],
            'school_competition': ['School', 'Sports', 'Competition', 'Drama'],
            
            # MILITARY/WAR BRIDGE CATEGORIES
            'military_action': ['Military', 'Action', 'War', 'Mecha'],
            'military_drama': ['Military', 'Drama', 'Historical', 'Tragedy'],
            'military_sci_fi': ['Military', 'Sci-Fi', 'Mecha', 'Space'],
            'war_psychological': ['War', 'Psychological', 'Drama', 'Thriller'],
            
            # MUSIC/ARTS BRIDGE CATEGORIES
            'music_drama': ['Music', 'Drama', 'Romance', 'Coming-of-Age'],
            'music_school': ['Music', 'School', 'Drama', 'Competition'],
            'performing_arts_drama': ['Performing Arts', 'Drama', 'Romance', 'Competition'],
            'idol_comedy': ['Idols (Female)', 'Comedy', 'Music', 'Slice of Life'],
            
            # MYSTERY BRIDGE CATEGORIES
            'mystery_horror': ['Mystery', 'Horror', 'Supernatural', 'Thriller'],
            'mystery_psychological': ['Mystery', 'Psychological', 'Thriller', 'Detective'],
            'mystery_supernatural': ['Mystery', 'Supernatural', 'Horror', 'Fantasy'],
            'detective_action': ['Detective', 'Action', 'Mystery', 'Crime'],
            'school_mystery': ['Mystery', 'School', 'Supernatural', 'Thriller'],
            
            # ADVENTURE BRIDGE CATEGORIES
            'survival_adventure': ['Adventure', 'Survival', 'Thriller', 'Action'],
            'fantasy_adventure': ['Adventure', 'Fantasy', 'Action', 'Magic'],
            'space_adventure': ['Adventure', 'Space', 'Sci-Fi', 'Action'],
            'historical_adventure': ['Adventure', 'Historical', 'Action', 'Drama'],
            
            # NICHE BRIDGE CATEGORIES
            'competitive_gaming': ['Strategy Game', 'Competition', 'Psychological', 'Drama'],
            'food_culture': ['Gourmet', 'Slice of Life', 'Comedy', 'Drama'],
            'otaku_culture': ['Otaku Culture', 'Comedy', 'Parody', 'Romance'],
            'coming_of_age': ['Coming-of-Age', 'Drama', 'School', 'Slice of Life'],
            'philosophy_existential': ['Philosophy', 'Psychological', 'Drama', 'Existential'],
            'tournament_battle': ['Tournament', 'Action', 'Competition', 'Super Power'],
            'team_friendship': ['Team Sports', 'Friendship', 'Drama', 'Coming-of-Age'],
            'artistic_expression': ['Art', 'Drama', 'Romance', 'Coming-of-Age']
        }
    
    def extract_advanced_features(self, df: pd.DataFrame) -> np.ndarray:
        """Enhanced feature extraction with better semantic understanding"""
        logger.info("Extracting advanced features...")
        
        # Prepare basic lists
        df["genres_list"] = df["genres"].apply(self.parse_list)
        df["themes_list"] = df["themes"].apply(self.parse_list)
        df["demographics_list"] = df["demographics"].apply(self.parse_list)
        
        feature_components = []
        self.feature_names = []
        
        # 1. Enhanced Genre Groups (Higher Priority)
        self.setup_enhanced_genre_groups()
        
        group_features = []
        for _, row in df.iterrows():
            all_tags = row["genres_list"] + row["themes_list"] + row["demographics_list"]
            all_tags_lower = [tag.lower() for tag in all_tags]
            
            group_vec = []
            for group_name, group_genres in self.genre_groups.items():
                # Weighted scoring: exact matches get full points, partial matches get partial
                exact_matches = sum(1 for genre in group_genres if genre.lower() in all_tags_lower)
                semantic_score = min(exact_matches / len(group_genres) * 1.5, 1.0)
                group_vec.append(semantic_score)
            
            group_features.append(group_vec)
        
        group_features = np.array(group_features, dtype=np.float32) * 4.0
        feature_components.append(group_features)
        self.feature_names.extend([f"genre_group_{name}" for name in self.genre_groups.keys()])
        logger.info(f"Genre group features: {group_features.shape[1]} dimensions")
        
        # 2. Individual Important Tags with TF-IDF weighting
        all_tags_flat = []
        for _, row in df.iterrows():
            tags = row["genres_list"] + row["themes_list"] + row["demographics_list"]
            all_tags_flat.extend([tag.lower() for tag in tags])
        
        tag_counts = Counter(all_tags_flat)
        # Select tags that appear in 10-1000 anime (not too rare, not too common)
        important_tags = [tag for tag, count in tag_counts.items() 
                         if 10 <= count <= 1000 and len(tag) > 2][:30]
        
        tag_features = []
        for _, row in df.iterrows():
            all_tags_lower = [tag.lower() for tag in 
                            row["genres_list"] + row["themes_list"] + row["demographics_list"]]
            
            # TF-IDF inspired weighting
            tag_vec = []
            for tag in important_tags:
                if tag in all_tags_lower:
                    # Inverse frequency weighting
                    weight = np.log(len(df) / tag_counts[tag])
                    tag_vec.append(weight)
                else:
                    tag_vec.append(0.0)
            tag_features.append(tag_vec)
        
        tag_features = np.array(tag_features, dtype=np.float32) * 2.5
        feature_components.append(tag_features)
        self.feature_names.extend([f"tag_{tag}" for tag in important_tags])
        logger.info(f"Individual tag features: {tag_features.shape[1]} dimensions")
        
        # 3. Advanced Synopsis Features with N-grams
        df['synopsis_clean'] = df['synopsis'].fillna('').apply(
            lambda x: re.sub(r'[^\w\s]', ' ', str(x).lower().strip())
        )
        
        try:
            # Two-stage TF-IDF: unigrams + bigrams
            tfidf_unigram = TfidfVectorizer(
                max_features=15,
                stop_words='english',
                min_df=10,
                max_df=0.6,
                ngram_range=(1, 1)
            )
            
            tfidf_bigram = TfidfVectorizer(
                max_features=10,
                stop_words='english', 
                min_df=5,
                max_df=0.7,
                ngram_range=(2, 2)
            )
            
            synopsis_unigram = tfidf_unigram.fit_transform(df['synopsis_clean']).toarray()
            synopsis_bigram = tfidf_bigram.fit_transform(df['synopsis_clean']).toarray()
            
            # Combine and compress
            synopsis_combined = np.hstack([synopsis_unigram, synopsis_bigram])
            if synopsis_combined.shape[1] > 20:
                svd = TruncatedSVD(n_components=20, random_state=42)
                synopsis_features = svd.fit_transform(synopsis_combined)
            else:
                synopsis_features = synopsis_combined
                
            synopsis_features = synopsis_features.astype(np.float32) * 2.0
            feature_components.append(synopsis_features)
            self.feature_names.extend([f"synopsis_dim_{i}" for i in range(synopsis_features.shape[1])])
            logger.info(f"Synopsis features: {synopsis_features.shape[1]} dimensions")
            
        except Exception as e:
            logger.warning(f"Synopsis features failed: {e}")
            synopsis_features = np.zeros((len(df), 8), dtype=np.float32)
            feature_components.append(synopsis_features)
            self.feature_names.extend([f"synopsis_dim_{i}" for i in range(8)])
        
        # 4. Enhanced Quality and Metadata Features
        quality_features = []
        for _, row in df.iterrows():
            features = []
            
            # Score with non-linear scaling
            score = row['score'] if pd.notna(row['score']) and row['score'] > 0 else 6.5
            score_norm = (score / 10.0) ** 1.2  # Emphasize higher scores
            features.append(score_norm)
                        
            # Member count (if available)
            members = row.get('members', 0)
            if pd.notna(members) and members > 0:
                member_score = min(np.log10(members) / 7, 1.0)
            else:
                member_score = 0.3
            features.append(member_score)
            
            # Type features (one-hot)
            type_features = [0] * 5
            type_map = {'TV': 0, 'Movie': 1, 'OVA': 2, 'Special': 3, 'ONA': 4}
            if row['type'] in type_map:
                type_features[type_map[row['type']]] = 1
            features.extend(type_features)
            
            # Episode count (normalized)
            episodes = row['episodes'] if pd.notna(row['episodes']) else 12
            episode_score = min(episodes / 100, 1.0) if episodes > 0 else 0.5
            features.append(episode_score)
            
            # Year features (era encoding)
            year = row['year'] if pd.notna(row['year']) else 2010
            era_features = [
                1 if year < 2000 else 0,  # Classic
                1 if 2000 <= year < 2010 else 0,  # 2000s
                1 if 2010 <= year < 2020 else 0,  # 2010s
                1 if year >= 2020 else 0   # Modern
            ]
            features.extend(era_features)
            
            quality_features.append(features)
        
        quality_features = np.array(quality_features, dtype=np.float32) * 1.8
        feature_components.append(quality_features)
        quality_names = ['score', 'members', 'type_tv', 'type_movie', 
                        'type_ova', 'type_special', 'type_ona', 'episodes', 
                        'era_classic', 'era_2000s', 'era_2010s', 'era_modern']
        self.feature_names.extend(quality_names)
        logger.info(f"Quality/Meta features: {quality_features.shape[1]} dimensions")
        
        # 5. Smart Studio Features with Reputation Weighting
        df["studios_list"] = df["studios"].apply(self.parse_list)
        all_studios = [studio for studios in df["studios_list"] for studio in studios]
        studio_counts = Counter(all_studios)
        
        # Studio reputation scores (manually curated based on industry recognition)
        studio_reputation = {
            'Studio Ghibli': 1.0, 'Madhouse': 0.95, 'Production I.G': 0.9,
            'Bones': 0.9, 'Kyoto Animation': 0.95, 'MAPPA': 0.85,
            'Wit Studio': 0.85, 'Trigger': 0.8, 'Shaft': 0.8, 'Pierrot': 0.7,
            'Toei Animation': 0.75, 'Sunrise': 0.8, 'A-1 Pictures': 0.7,
            'J.C.Staff': 0.65, 'Studio Deen': 0.6, 'Gainax': 0.85
        }
        
        # Select studios by combination of frequency and reputation
        selected_studios = []
        for studio, count in studio_counts.items():
            reputation_score = studio_reputation.get(studio, 0.5)
            combined_score = (count / 50) * reputation_score  # Normalize count by 50
            if combined_score > 0.1 or count >= 15:
                selected_studios.append(studio)
        
        selected_studios = selected_studios[:25]  # Limit to top 25
        
        studio_features = []
        for _, row in df.iterrows():
            studio_vec = []
            for studio in selected_studios:
                if studio in row["studios_list"]:
                    weight = studio_reputation.get(studio, 0.5)
                    studio_vec.append(weight)
                else:
                    studio_vec.append(0.0)
            studio_features.append(studio_vec)
        
        studio_features = np.array(studio_features, dtype=np.float32) * 0.8
        feature_components.append(studio_features)
        self.feature_names.extend([f"studio_{studio.replace(' ', '_')}" for studio in selected_studios])
        logger.info(f"Studio features: {studio_features.shape[1]} dimensions ({len(selected_studios)} studios)")
        
        # Combine all features
        final_features = np.hstack(feature_components)
        logger.info(f"Final feature matrix: {final_features.shape}")
        
        return final_features.astype(np.float32)
    
    def build_clusters(self, features: np.ndarray, n_clusters: int = 50) -> None:
        """Build clusters for diversity in recommendations"""
        logger.info(f"Building {n_clusters} clusters...")
        
        # Standardize features for clustering
        self.scaler = StandardScaler()
        features_scaled = self.scaler.fit_transform(features)
        
        # K-means clustering
        self.cluster_model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.clusters = self.cluster_model.fit_predict(features_scaled)
        
        logger.info(f"Clustering completed. Cluster distribution: {Counter(self.clusters)}")
    
    def build_and_save_model(self, csv_path: str = "animes.csv", compress: bool = True) -> bool:
        """Build and save the enhanced model"""
        try:
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            full_csv_path = os.path.join(BASE_DIR, csv_path)
            
            if not os.path.exists(full_csv_path):
                logger.error(f"CSV file not found: {full_csv_path}")
                return False
            
            logger.info(f"Loading data from {full_csv_path}")
            df = pd.read_csv(full_csv_path)
            
            # Data cleaning with better error handling
            numeric_cols = ['score', 'members', 'episodes', 'year']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Extract features
            features = self.extract_advanced_features(df)
            
            # Build clusters if enabled
            if self.config.use_clustering:
                self.build_clusters(features)
            
            # Prepare minimal dataset for deployment
            essential_cols = [
                'mal_id', 'title', 'title_english', 'score', 'type', 'episodes',
                'year', 'genres', 'themes', 'demographics', 'synopsis', 'studios'
            ]
            df_minimal = df[[col for col in essential_cols if col in df.columns]].copy()
            
            # Optimize synopsis length
            if 'synopsis' in df_minimal.columns:
                df_minimal['synopsis'] = df_minimal['synopsis'].apply(
                    lambda x: str(x)[:400] + '...' if isinstance(x, str) and len(str(x)) > 400 else x
                )
            
            # Model metadata
            self.model_info = {
                'version': '6.0-advanced',
                'feature_count': features.shape[1],
                'anime_count': len(df_minimal),
                'compression': compress,
                'build_date': datetime.now().isoformat(),
                'use_clustering': self.config.use_clustering,
                'n_clusters': len(set(self.clusters)) if self.clusters is not None else 0,
                'feature_names': self.feature_names
            }
            
            # Save model
            model_data = {
                'df': df_minimal,
                'features': features,
                'clusters': self.clusters,
                'cluster_model': self.cluster_model,
                'scaler': self.scaler,
                'model_info': self.model_info,
                'genre_groups': self.genre_groups,
                'feature_names': self.feature_names,
                'config': asdict(self.config)
            }
            
            filename = "anime_recommender_advanced.pkl"
            if compress:
                filename += ".gz"
                with gzip.open(filename, "wb") as f:
                    pickle.dump(model_data, f, protocol=pickle.HIGHEST_PROTOCOL)
            else:
                with open(filename, "wb") as f:
                    pickle.dump(model_data, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            file_size = os.path.getsize(filename) / 1024 / 1024
            logger.info(f"Advanced model saved: {filename}")
            logger.info(f"Features: {features.shape}, File size: {file_size:.2f} MB")
            
            return True
            
        except Exception as e:
            logger.error(f"Error building model: {e}")
            return False
    
    def load_model(self, model_path: str = "anime_recommender_advanced.pkl.gz") -> bool:
        """Load the model with better error handling"""
        try:
            if model_path.endswith('.gz'):
                with gzip.open(model_path, "rb") as f:
                    model_data = pickle.load(f)
            else:
                with open(model_path, "rb") as f:
                    model_data = pickle.load(f)
            
            self.df = model_data['df']
            self.features = model_data['features']
            self.clusters = model_data.get('clusters')
            self.cluster_model = model_data.get('cluster_model')
            self.scaler = model_data.get('scaler')
            self.model_info = model_data.get('model_info', {})
            self.genre_groups = model_data.get('genre_groups', {})
            self.feature_names = model_data.get('feature_names', [])
            
            # Load config if available
            if 'config' in model_data:
                self.config = RecommendationConfig(**model_data['config'])
            
            logger.info(f"Model loaded: {self.model_info.get('version', 'Unknown')}")
            logger.info(f"Dataset: {len(self.df)} anime, {self.features.shape[1]} features")
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def get_cluster_recommendations(self, source_idx: int, top_k: int = 50) -> List[int]:
        """Get diverse recommendations using clustering"""
        if self.clusters is None:
            return []
        
        source_cluster = self.clusters[source_idx]
        
        # Get anime from same cluster (similar) and different clusters (diverse)
        same_cluster_indices = np.where(self.clusters == source_cluster)[0]
        different_cluster_indices = np.where(self.clusters != source_cluster)[0]
        
        # Mix: 70% from same cluster, 30% from different clusters
        same_cluster_sample = np.random.choice(
            same_cluster_indices, 
            size=min(int(top_k * 0.7), len(same_cluster_indices)), 
            replace=False
        )
        different_cluster_sample = np.random.choice(
            different_cluster_indices,
            size=min(int(top_k * 0.3), len(different_cluster_indices)),
            replace=False
        )
        
        return np.concatenate([same_cluster_sample, different_cluster_sample]).tolist()
    
    def explain_similarity_enhanced(self, source_anime: pd.Series, target_anime: pd.Series) -> str:
        """Enhanced explanation with more detailed analysis"""
        # Use cache if available
        cache_key = (int(source_anime['mal_id']), int(target_anime['mal_id']))
        if cache_key in self._explanation_cache:
            return self._explanation_cache[cache_key]
        
        source_genres = set(self.parse_list(source_anime.get('genres', '')))
        target_genres = set(self.parse_list(target_anime.get('genres', '')))
        source_themes = set(self.parse_list(source_anime.get('themes', '')))
        target_themes = set(self.parse_list(target_anime.get('themes', '')))
        
        explanation_parts = []
        
        # Genre analysis
        common_genres = source_genres & target_genres
        if common_genres:
            if len(common_genres) >= 3:
                explanation_parts.append(f"Strong genre overlap: {', '.join(list(common_genres)[:3])}")
            elif len(common_genres) == 2:
                explanation_parts.append(f"Shared genres: {', '.join(common_genres)}")
            else:
                explanation_parts.append(f"Same genre: {list(common_genres)[0]}")
        
        # Theme analysis
        common_themes = source_themes & target_themes
        if common_themes:
            if len(common_themes) >= 2:
                explanation_parts.append(f"Similar themes: {', '.join(list(common_themes)[:2])}")
            else:
                explanation_parts.append(f"Shared theme: {list(common_themes)[0]}")
        
        # Semantic group analysis
        source_all_tags = list(source_genres) + list(source_themes)
        target_all_tags = list(target_genres) + list(target_themes)
        
        for group_name, group_tags in self.genre_groups.items():
            source_matches = sum(1 for tag in group_tags if tag in source_all_tags)
            target_matches = sum(1 for tag in group_tags if tag in target_all_tags)
            
            if source_matches >= 2 and target_matches >= 2:
                group_display = group_name.replace('_', ' ').title()
                explanation_parts.append(f"Both fit {group_display} category")
                break
        
        # Format and era analysis
        if source_anime.get('type') == target_anime.get('type'):
            if source_anime.get('type') in ['TV', 'Movie']:
                explanation_parts.append(f"Both {source_anime.get('type')} format")
        
        # Score tier analysis
        source_score = source_anime.get('score', 0)
        target_score = target_anime.get('score', 0)
        if pd.notna(source_score) and pd.notna(target_score):
            if source_score >= 8.5 and target_score >= 8.5:
                explanation_parts.append("Both highly acclaimed")
            elif source_score >= 8.0 and target_score >= 8.0:
                explanation_parts.append("Both well-rated")
            elif abs(source_score - target_score) <= 0.5:
                explanation_parts.append("Similar rating levels")
        
        # Year proximity
        source_year = source_anime.get('year')
        target_year = target_anime.get('year')
        if pd.notna(source_year) and pd.notna(target_year):
            year_diff = abs(int(source_year) - int(target_year))
            if year_diff <= 2:
                explanation_parts.append(f"Same period ({int(target_year)})")
            elif year_diff <= 5:
                explanation_parts.append("Similar era")
        
        # Studio connection
        source_studios = set(self.parse_list(source_anime.get('studios', '')))
        target_studios = set(self.parse_list(target_anime.get('studios', '')))
        common_studios = source_studios & target_studios
        if common_studios:
            explanation_parts.append(f"Same studio: {list(common_studios)[0]}")
        
        # Combine explanation
        if explanation_parts:
            explanation = "; ".join(explanation_parts[:4])  # Limit to 4 reasons
        else:
            explanation = "Similar content profile and style"
        
        # Cache the result
        self._explanation_cache[cache_key] = explanation
        return explanation
    
    def recommend(self, anime_mal_id: int, config: Optional[RecommendationConfig] = None) -> Dict[str, Any]:
        """
        Enhanced recommendation function with configurable parameters
        """
        if config:
            self.config = config
        
        if self.df is None or self.features is None:
            return {"error": "Model not loaded"}
        
        if anime_mal_id not in self.df["mal_id"].values:
            return {"error": f"Anime ID {anime_mal_id} not found"}
        
        try:
            # Get source anime
            source_idx = self.df[self.df["mal_id"] == anime_mal_id].index[0]
            source_anime = self.df.iloc[source_idx]
            
            # Calculate similarities with caching
            cache_key = (anime_mal_id, "similarities")
            if hasattr(self, '_sim_cache') and cache_key in self._sim_cache:
                sim_scores = self._sim_cache[cache_key]
            else:
                sim_scores = cosine_similarity([self.features[source_idx]], self.features)[0]
                if not hasattr(self, '_sim_cache'):
                    self._sim_cache = {}
                self._sim_cache[cache_key] = sim_scores
            
            # Add clustering diversity if enabled
            if self.config.use_clustering and self.clusters is not None:
                cluster_candidates = self.get_cluster_recommendations(source_idx, self.config.top_k * 3)
                cluster_boost = np.zeros_like(sim_scores)
                cluster_boost[cluster_candidates] = self.config.cluster_weight
                sim_scores = sim_scores + cluster_boost
            
            # Add diversity factor
            if self.config.diversity_factor > 0:
                noise = np.random.normal(0, self.config.diversity_factor, len(sim_scores))
                sim_scores = sim_scores + noise
            
            # Create results dataframe
            results_df = self.df.copy()
            results_df['similarity'] = sim_scores
            
            # Remove source anime
            results_df = results_df[results_df['mal_id'] != anime_mal_id]
            
            # Apply filters
            if self.config.min_score > 0:
                results_df = results_df[
                    (results_df['score'] >= self.config.min_score) | 
                    results_df['score'].isna()
                ]
            
            # Remove sequels if requested
            if not self.config.include_sequels:
                source_title_words = source_anime['title'].lower().split()
                if len(source_title_words) > 0:
                    main_title = source_title_words[0]
                    if len(main_title) > 3:
                        mask = ~results_df['title'].str.lower().str.contains(
                            main_title, na=False, regex=False
                        )
                        results_df = results_df[mask]
            
            # Enhanced scoring with multiple factors
            results_df['quality_score'] = results_df['score'].fillna(6.5) / 10.0
            
            # Final weighted score
            results_df['final_score'] = (
                results_df['similarity'] * 0.6 +
                results_df['quality_score'] * 0.25
            )
            
            # Get top recommendations
            top_recs = results_df.nlargest(self.config.top_k, 'final_score')
            
            # Format recommendations
            recommendations = []
            for idx, (_, row) in enumerate(top_recs.iterrows()):
                rec = AnimeInfo(
                    mal_id=int(row['mal_id']),
                    title=row['title'],
                    title_english=row.get('title_english', ''),
                    score=float(row['score']) if pd.notna(row['score']) else None,
                    type=row['type'],
                    episodes=int(row['episodes']) if pd.notna(row['episodes']) else None,
                    year=int(row['year']) if pd.notna(row['year']) else None,
                    genres=self.parse_list(row.get('genres', '')),
                    themes=self.parse_list(row.get('themes', '')),
                    synopsis=self._truncate_synopsis(row.get('synopsis', '')),
                    similarity=float(row['similarity'])
                )
                
                # Add explanation if requested
                if self.config.explain:
                    rec.explanation = self.explain_similarity_enhanced(source_anime, row)
                
                recommendations.append(asdict(rec))
            
            return {
                'source': asdict(AnimeInfo(
                    mal_id=int(source_anime['mal_id']),
                    title=source_anime['title'],
                    title_english=source_anime.get('title_english', ''),
                    score=float(source_anime['score']) if pd.notna(source_anime['score']) else None,
                    type=source_anime['type'],
                    episodes=int(source_anime['episodes']) if pd.notna(source_anime['episodes']) else None,
                    year=int(source_anime['year']) if pd.notna(source_anime['year']) else None,
                    genres=self.parse_list(source_anime.get('genres', '')),
                    themes=self.parse_list(source_anime.get('themes', '')),
                    synopsis=self._truncate_synopsis(source_anime.get('synopsis', ''))
                )),
                'recommendations': recommendations,
                'total_found': len(results_df),
                'parameters': asdict(self.config),
                'model_info': {
                    'version': self.model_info.get('version', 'Unknown'),
                    'feature_count': self.features.shape[1],
                    'use_clustering': self.config.use_clustering
                }
            }
            
        except Exception as e:
            logger.error(f"Error in recommendation: {e}")
            return {"error": f"Recommendation failed: {str(e)}"}
    
    def _truncate_synopsis(self, synopsis: str, max_length: int = 200) -> str:
        """Helper to truncate synopsis"""
        if not isinstance(synopsis, str) or len(synopsis) <= max_length:
            return synopsis or ""
        return synopsis[:max_length].rsplit(' ', 1)[0] + '...'
    
    def batch_recommend(self, anime_mal_ids: List[int], 
                       config: Optional[RecommendationConfig] = None) -> Dict[int, Dict[str, Any]]:
        """Get recommendations for multiple anime efficiently"""
        results = {}
        for mal_id in anime_mal_ids:
            results[mal_id] = self.recommend(mal_id, config)
        return results
    
    def get_similar_by_features(self, features: Dict[str, Any], top_k: int = 10) -> Dict[str, Any]:
        """Find anime similar to given feature preferences"""
        if self.df is None or self.features is None:
            return {"error": "Model not loaded"}
        
        try:
            # Create feature vector from preferences
            preference_vector = np.zeros(self.features.shape[1])
            
            # Map preferences to feature indices
            for feature_name, weight in features.items():
                if feature_name in self.feature_names:
                    idx = self.feature_names.index(feature_name)
                    preference_vector[idx] = weight
            
            # Find most similar anime
            similarities = cosine_similarity([preference_vector], self.features)[0]
            
            # Get top matches
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            recommendations = []
            for idx in top_indices:
                row = self.df.iloc[idx]
                rec = AnimeInfo(
                    mal_id=int(row['mal_id']),
                    title=row['title'],
                    title_english=row.get('title_english', ''),
                    score=float(row['score']) if pd.notna(row['score']) else None,
                    similarity=float(similarities[idx])
                )
                recommendations.append(asdict(rec))
            
            return {
                'recommendations': recommendations,
                'query_features': features
            }
            
        except Exception as e:
            logger.error(f"Error in feature-based search: {e}")
            return {"error": f"Feature search failed: {str(e)}"}
    
    def get_anime_info(self, mal_id: int) -> Dict[str, Any]:
        """Get detailed info about a specific anime with cluster information"""
        if mal_id not in self.df["mal_id"].values:
            return {"error": "Anime not found"}
        
        anime = self.df[self.df["mal_id"] == mal_id].iloc[0]
        anime_idx = self.df[self.df["mal_id"] == mal_id].index[0]
        
        info = asdict(AnimeInfo(
            mal_id=int(anime['mal_id']),
            title=anime['title'],
            title_english=anime.get('title_english', ''),
            score=float(anime['score']) if pd.notna(anime['score']) else None,
            type=anime['type'],
            episodes=int(anime['episodes']) if pd.notna(anime['episodes']) else None,
            year=int(anime['year']) if pd.notna(anime['year']) else None,
            genres=self.parse_list(anime.get('genres', '')),
            themes=self.parse_list(anime.get('themes', '')),
            synopsis=anime.get('synopsis', '')
        ))
        
        # Add cluster information if available
        if self.clusters is not None:
            cluster_id = int(self.clusters[anime_idx])
            cluster_size = int(np.sum(self.clusters == cluster_id))
            info['cluster_info'] = {
                'cluster_id': cluster_id,
                'cluster_size': cluster_size
            }
        
        return info
    
    def get_cluster_analysis(self, cluster_id: int, top_k: int = 20) -> Dict[str, Any]:
        """Analyze a specific cluster to understand its characteristics"""
        if self.clusters is None:
            return {"error": "Clustering not available"}
        
        cluster_indices = np.where(self.clusters == cluster_id)[0]
        if len(cluster_indices) == 0:
            return {"error": "Cluster not found"}
        
        cluster_anime = self.df.iloc[cluster_indices]
        
        # Analyze genres and themes
        all_genres = []
        all_themes = []
        for _, row in cluster_anime.iterrows():
            all_genres.extend(self.parse_list(row.get('genres', '')))
            all_themes.extend(self.parse_list(row.get('themes', '')))
        
        genre_counts = Counter(all_genres)
        theme_counts = Counter(all_themes)
        
        # Get representative anime (highest scoring)
        top_anime = cluster_anime.nlargest(min(top_k, len(cluster_anime)), 'score')
        
        return {
            'cluster_id': cluster_id,
            'size': len(cluster_indices),
            'top_genres': dict(genre_counts.most_common(10)),
            'top_themes': dict(theme_counts.most_common(10)),
            'avg_score': float(cluster_anime['score'].mean()),
            'representative_anime': [
                {
                    'mal_id': int(row['mal_id']),
                    'title': row['title'],
                    'score': float(row['score']) if pd.notna(row['score']) else None
                }
                for _, row in top_anime.iterrows()
            ]
        }
    
    def search_anime(self, query: str, search_fields: List[str] = None, top_k: int = 20) -> Dict[str, Any]:
        """Search anime by title, genres, or themes"""
        if self.df is None:
            return {"error": "Model not loaded"}
        
        search_fields = search_fields or ['title', 'title_english', 'genres', 'themes']
        query_lower = query.lower()
        
        results = []
        for _, row in self.df.iterrows():
            score = 0
            matches = []
            
            # Title matching
            if 'title' in search_fields and query_lower in row['title'].lower():
                score += 10
                matches.append('title')
            
            if 'title_english' in search_fields and pd.notna(row.get('title_english')):
                if query_lower in row['title_english'].lower():
                    score += 8
                    matches.append('english_title')
            
            # Genre/theme matching
            if 'genres' in search_fields:
                genres = self.parse_list(row.get('genres', ''))
                if any(query_lower in genre.lower() for genre in genres):
                    score += 5
                    matches.append('genre')
            
            if 'themes' in search_fields:
                themes = self.parse_list(row.get('themes', ''))
                if any(query_lower in theme.lower() for theme in themes):
                    score += 3
                    matches.append('theme')
            
            if score > 0:
                results.append({
                    'anime': asdict(AnimeInfo(
                        mal_id=int(row['mal_id']),
                        title=row['title'],
                        title_english=row.get('title_english', ''),
                        score=float(row['score']) if pd.notna(row['score']) else None,
                        type=row['type'],
                        year=int(row['year']) if pd.notna(row['year']) else None,
                        genres=self.parse_list(row.get('genres', '')),
                        themes=self.parse_list(row.get('themes', ''))
                    )),
                    'search_score': score,
                    'match_types': matches
                })
        
        # Sort by search score and quality
        results.sort(key=lambda x: (x['search_score'], x['anime']['score'] or 0), reverse=True)
        
        return {
            'query': query,
            'results': results[:top_k],
            'total_found': len(results)
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        status = {
            'status': 'healthy' if self.df is not None else 'not_loaded',
            'model_info': self.model_info,
            'anime_count': len(self.df) if self.df is not None else 0,
            'feature_count': self.features.shape[1] if self.features is not None else 0,
            'clustering_enabled': self.clusters is not None,
            'cache_size': len(self._explanation_cache),
            'config': asdict(self.config)
        }
        
        # Add memory usage estimation
        if self.features is not None:
            memory_mb = (self.features.nbytes + 
                        (self.clusters.nbytes if self.clusters is not None else 0)) / 1024 / 1024
            status['memory_usage_mb'] = round(memory_mb, 2)
        
        return status
    
    def get_feature_importance(self, anime_mal_id: int, top_k: int = 10) -> Dict[str, Any]:
        """Analyze which features are most important for this anime"""
        if anime_mal_id not in self.df["mal_id"].values:
            return {"error": "Anime not found"}
        
        anime_idx = self.df[self.df["mal_id"] == anime_mal_id].index[0]
        anime_features = self.features[anime_idx]
        
        # Get feature importance (non-zero features)
        feature_importance = []
        for i, (name, value) in enumerate(zip(self.feature_names, anime_features)):
            if abs(value) > 0.001:  # Only significant features
                feature_importance.append({
                    'feature': name,
                    'value': float(value),
                    'normalized': float(value / np.max(np.abs(anime_features)))
                })
        
        # Sort by absolute value
        feature_importance.sort(key=lambda x: abs(x['value']), reverse=True)
        
        return {
            'anime_id': anime_mal_id,
            'title': self.df[self.df["mal_id"] == anime_mal_id].iloc[0]['title'],
            'top_features': feature_importance[:top_k],
            'total_features': len([f for f in anime_features if abs(f) > 0.001])
        }

def main():
    """Enhanced main function with comprehensive testing"""
    # Create recommender with custom config
    config = RecommendationConfig(
        top_k=15,
        min_score=7.0,
        include_sequels=False,
        diversity_factor=0.05,
        explain=True,
        use_clustering=True,
        cluster_weight=0.15
    )
    
    recommender = AdvancedAnimeRecommender(config)
    
    # Build model
    logger.info("Building advanced model...")
    if recommender.build_and_save_model("animes.csv", compress=True):
        logger.info("Model built successfully!")
    else:
        logger.error("Failed to build model")
        return
    
    # Test loading and functionality
    logger.info("Testing model...")
    if not recommender.load_model():
        logger.error("Failed to load model")
        return
    
    # Health check
    health = recommender.health_check()
    logger.info(f"Health Status: {health['status']}")
    logger.info(f"Memory Usage: {health.get('memory_usage_mb', 'N/A')} MB")
    
    # Test recommendations
    test_anime_id = 85  
    result = recommender.recommend(test_anime_id)
    
    if 'error' not in result:
        logger.info(f"\nRecommendations for: {result['source']['title']}")
        logger.info(f"Found {result['total_found']} potential matches")
        
        for i, rec in enumerate(result['recommendations'][:15], 1):
            logger.info(f"{i}. {rec['title']} ({rec['score']}/10)")
            logger.info(f"   Similarity: {rec['similarity']:.3f}")
            if rec.get('explanation'):
                logger.info(f"   Why: {rec['explanation']}")
            logger.info("")
        
        # Test feature importance
        importance = recommender.get_feature_importance(test_anime_id)
        if 'error' not in importance:
            logger.info(f"\nTop features for {importance['title']}:")
            for feat in importance['top_features'][:5]:
                logger.info(f"  {feat['feature']}: {feat['value']:.3f}")
        
        # Test search
        search_result = recommender.search_anime("mecha", top_k=5)
        if 'error' not in search_result:
            logger.info(f"\nSearch results for 'mecha': {search_result['total_found']} found")
            for result_item in search_result['results'][:3]:
                logger.info(f"  {result_item['anime']['title']} (matches: {result_item['match_types']})")
        
        # Test cluster analysis if clustering is enabled
        if recommender.clusters is not None:
            cluster_id = int(recommender.clusters[0]) 
            cluster_info = recommender.get_cluster_analysis(cluster_id)
            if 'error' not in cluster_info:
                logger.info(f"\nCluster {cluster_id} analysis:")
                logger.info(f"  Size: {cluster_info['size']} anime")
                logger.info(f"  Avg Score: {cluster_info['avg_score']:.2f}")
                logger.info(f"  Top genres: {list(cluster_info['top_genres'].keys())[:3]}")
    else:
        logger.error(f"Recommendation error: {result['error']}")

if __name__ == "__main__":
    main()