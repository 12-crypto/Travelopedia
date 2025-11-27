"""personalization_gnn.py
Lightweight GNN-like personalization module.

This module is designed to be dependency-light and self-contained for the
Travelopedia project. It provides a simple graph-based preprocessing
pipeline, deterministic embedding generation and utilities for ranking and
explaining recommendations. The implementation is intentionally not
dependent on PyTorch Geometric so it remains runnable in environments
without heavy graph libraries. If `torch` is available we expose a small
hook to plug in a learned model later.
"""

from __future__ import annotations

import math
import os
import random
from typing import Dict, List, Any, Optional

import yaml

from backend.utils.logger import get_logger

logger = get_logger(__name__)


class PersonalizationGNN:
    """Graph-based personalization helper.

    Responsibilities:
    - Build a compact graph representation from user profile + history
    - Produce a deterministic, reproducible user embedding vector
    - Rank options (hotels/flights/activities) using the embedding
    - Explain recommendations

    The implementation deliberately avoids heavy ML dependencies so the
    rest of the backend can call into it without requiring GPU or
    PyG/PyTorch. A future enhancement can detect `torch` and load a
    trained GNN model.
    """

    def __init__(self, config_path: str = "backend/utils/config.yaml"):
        with open(config_path, "r") as fh:
            self.config = yaml.safe_load(fh)

        # Personalization hyperparams (provide sane defaults)
        pconf = self.config.get("personalization", {}) if isinstance(self.config, dict) else {}
        self.embedding_dim: int = int(pconf.get("user_embedding_dim", 64))
        self.seed = int(pconf.get("random_seed", 42))
        random.seed(self.seed)

        # simple caches
        self.user_embeddings: Dict[str, List[float]] = {}

        logger.info("PersonalizationGNN initialized (lightweight)")

    # --------------------------- Graph building ---------------------------
    def build_preference_graph(self, user_id: str, preferences: Dict[str, Any], history: Dict[str, Any]) -> Dict[str, Any]:
        """Builds a simple graph dict capturing user, preference and destination nodes.

        The returned structure is lightweight and intended for deterministic
        feature extraction rather than feeding directly to a library.
        """
        logger.debug("build_preference_graph: user=%s", user_id)

        nodes: List[Dict[str, Any]] = []
        edges: List[Dict[str, Any]] = []

        # user node
        nodes.append({"id": user_id, "type": "user"})

        # preference nodes
        categories = []
        if isinstance(preferences, dict):
            categories = preferences.get("categories", []) or preferences.get("interests", []) or []

        for cat in categories:
            nid = f"pref:{cat}"
            nodes.append({"id": nid, "type": "preference", "category": cat})
            edges.append({"source": user_id, "target": nid, "weight": 1.0})

        # destinations from history
        prev_trips = []
        if isinstance(history, dict):
            prev_trips = history.get("previous_trips", []) or history.get("trips", [])

        for i, trip in enumerate(prev_trips):
            dest_name = trip.get("destination") if isinstance(trip, dict) else str(trip)
            nid = f"dest:{i}:{dest_name}"
            sat = float(trip.get("satisfaction", 0)) if isinstance(trip, dict) else 0.0
            nodes.append({"id": nid, "type": "destination", "name": dest_name, "satisfaction": sat})
            edges.append({"source": user_id, "target": nid, "weight": max(0.0, min(1.0, sat / 5.0))})

            prefs = trip.get("preferences", []) if isinstance(trip, dict) else []
            for pref in prefs:
                pid = f"pref:{pref}"
                # only add edge if pref node exists
                if any(n.get("id") == pid for n in nodes):
                    edges.append({"source": nid, "target": pid, "weight": 0.8})

        graph = {"nodes": nodes, "edges": edges}
        logger.debug("Graph built nodes=%d edges=%d", len(nodes), len(edges))
        return graph

    # --------------------------- Embeddings ------------------------------
    def generate_user_embedding(self, user_id: str, preference_graph: Dict[str, Any]) -> List[float]:
        """Deterministic embedding from graph features.

        This function converts categorical counts and satisfaction statistics
        into a fixed-length vector. It is reproducible and robust across
        environments where heavy ML libraries might not be present.
        """
        if user_id in self.user_embeddings:
            return self.user_embeddings[user_id]

        # Basic features: counts of preferences, avg satisfaction, number of trips
        pref_counts: Dict[str, int] = {}
        sats: List[float] = []

        for node in preference_graph.get("nodes", []):
            if node.get("type") == "preference":
                cat = str(node.get("category", "")).lower()
                pref_counts[cat] = pref_counts.get(cat, 0) + 1
            elif node.get("type") == "destination":
                sats.append(float(node.get("satisfaction", 0)))

        avg_sat = float(sum(sats) / len(sats)) if sats else 0.0
        num_trips = len(sats)

        # deterministic pseudo-random vector seeded by user id and counts
        seed_val = abs(hash(user_id)) % (2 ** 32)
        rng = random.Random(seed_val + self.seed)

        vec: List[float] = []

        # slot 1..k: top-k preference counts hashed into vector
        sorted_prefs = sorted(pref_counts.items(), key=lambda x: (-x[1], x[0]))
        for i in range(min(len(sorted_prefs), self.embedding_dim // 4)):
            cat, cnt = sorted_prefs[i]
            v = (hash(cat) % 1000) / 1000.0
            vec.append((cnt + v) * (1.0 + (i * 0.01)))

        # fill remaining slots with rng values influenced by avg_sat and trips
        while len(vec) < self.embedding_dim:
            # mix deterministic and random
            r = rng.random() * (1.0 + avg_sat / 5.0) * (1.0 + num_trips * 0.01)
            vec.append(r)

        # normalize
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        embedding = [float(x / norm) for x in vec[: self.embedding_dim]]

        self.user_embeddings[user_id] = embedding
        logger.debug("Generated embedding dim=%d for user=%s", len(embedding), user_id)
        return embedding

    # --------------------------- Ranking --------------------------------
    def rank_options(self, user_embedding: List[float], options: List[Dict[str, Any]], option_type: str = "hotel") -> List[Dict[str, Any]]:
        """Score and rank candidate options.

        The scoring function uses lightweight heuristics combined with a
        cosine-similarity-like score between a deterministic option vector
        and the user embedding.
        """
        logger.debug("rank_options: type=%s count=%d", option_type, len(options))
        scored: List[Dict[str, Any]] = []

        for opt in options:
            if not isinstance(opt, dict):
                continue
            opt_vec = self._option_to_vector(opt, option_type, dim=len(user_embedding))
            sim = self._cosine_similarity(user_embedding, opt_vec)
            base = float(opt.get("rating", 3.5)) / 5.0 if opt.get("rating") is not None else 0.5
            score = 0.6 * sim + 0.4 * base
            # clamp
            score = max(0.0, min(1.0, score))

            entry = dict(opt)
            entry["personalization_score"] = score
            scored.append(entry)

        scored.sort(key=lambda x: x["personalization_score"], reverse=True)
        return scored

    def _option_to_vector(self, option: Dict[str, Any], option_type: str, dim: int) -> List[float]:
        """Deterministic vectorization for an option.

        Uses simple features: rating, price, stops/stay length, and hashed
        categorical tokens (amenities, category). Output is length `dim`.
        """
        if dim <= 0:
            return []

        vec = [0.0] * dim
        rating = float(option.get("rating", 3.5)) / 5.0
        price = float(option.get("price", option.get("price_total", 0) or 0))
        price_norm = 1.0 / (1.0 + math.log(1 + price)) if price >= 1 else 1.0
        vec[0] = rating
        vec[1 % dim] = price_norm

        # token hashing into vector slots
        tokens = []
        if option_type == "hotel":
            tokens += option.get("amenities", []) or []
            tokens.append(option.get("room_type", ""))
        elif option_type == "flight":
            outbound = option.get("outbound", {})
            stops = int(outbound.get("stops", 0))
            dur = float(outbound.get("duration_hours", outbound.get("duration", 0)))
            vec[2 % dim] = max(0.0, 1.0 - (stops * 0.15))
            vec[3 % dim] = 1.0 / (1.0 + dur) if dur > 0 else 0.0
            tokens.append(str(stops))
        else:
            tokens.append(option.get("category", ""))

        # scatter hashed tokens
        for t in tokens:
            if not t:
                continue
            h = abs(hash(str(t)))
            idx = (h % (dim - 4)) + 4
            vec[idx % dim] += (h % 1000) / 1000.0

        # normalize
        n = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [float(x / n) for x in vec]

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        if not a or not b:
            return 0.0
        m = min(len(a), len(b))
        num = sum(a[i] * b[i] for i in range(m))
        na = math.sqrt(sum(a[i] * a[i] for i in range(m))) or 1.0
        nb = math.sqrt(sum(b[i] * b[i] for i in range(m))) or 1.0
        return float(num / (na * nb))

    # --------------------------- Activities --------------------------------
    def recommend_activities(self, user_profile: Dict[str, Any], destination: str, available_activities: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """Return ranked activities for a user at a destination."""
        logger.debug("recommend_activities: dest=%s", destination)
        acts = available_activities if available_activities is not None else self._generate_mock_activities(user_profile, destination)

        # build a user embedding
        graph = self.build_preference_graph(user_profile.get("id", "anon"), user_profile.get("preferences", {}), user_profile.get("history", {}))
        emb = self.generate_user_embedding(user_profile.get("id", "anon"), graph)

        ranked = []
        for a in acts:
            score = self._calculate_activity_score(a, user_profile.get("preferences", {}).get("categories", []) if isinstance(user_profile.get("preferences", {}), dict) else user_profile.get("preferences", []))
            # combine with embedding similarity
            a_vec = self._option_to_vector(a, "activity", dim=len(emb))
            sim = self._cosine_similarity(emb, a_vec)
            final = 0.5 * (score / 100.0) + 0.5 * sim
            e = dict(a)
            e["personalization_score"] = max(0.0, min(1.0, final))
            ranked.append(e)

        ranked.sort(key=lambda x: x.get("personalization_score", 0.0), reverse=True)
        return ranked[:10]

    def _calculate_activity_score(self, activity: Dict[str, Any], preferences: List[str]) -> float:
        rating = float(activity.get("rating", 4.0))
        price_level = int(activity.get("price_level", activity.get("price_level", 2)))
        base = (rating / 5.0) * 100.0
        category = str(activity.get("category", "")).lower()
        if any(category == p.lower() for p in (preferences or [])):
            base += 30
        base -= (price_level - 1) * 5
        return max(0.0, base)

    def _generate_mock_activities(self, user_profile: Dict[str, Any], destination: str) -> List[Dict[str, Any]]:
        activity_types = {
            "adventure": ["Hiking", "Zip-lining", "Kayaking", "Rock Climbing"],
            "cultural": ["Museum Visit", "Historical Tour", "Art Gallery", "Local Market"],
            "culinary": ["Food Tour", "Cooking Class", "Wine Tasting", "Local Restaurant"],
            "nature": ["Beach Visit", "Park Walk", "Botanical Garden", "Scenic Viewpoint"],
            "relaxation": ["Spa Day", "Yoga Class", "Meditation", "Beach Relaxation"],
        }

        prefs = []
        if isinstance(user_profile.get("preferences", {}), dict):
            prefs = user_profile.get("preferences", {}).get("categories", []) or []
        elif isinstance(user_profile.get("preferences", []), list):
            prefs = user_profile.get("preferences", [])

        out: List[Dict[str, Any]] = []
        for cat, examples in activity_types.items():
            for idx, name in enumerate(examples[:3]):
                a = {
                    "id": f"{destination}:{cat}:{idx}",
                    "name": name + f" in {destination}",
                    "category": cat,
                    "rating": round(3.5 + random.random() * 1.5, 1),
                    "price_level": random.randint(1, 3),
                }
                out.append(a)

        # bias generation order by user prefs
        if prefs:
            out.sort(key=lambda x: 0 if x["category"] in [p.lower() for p in prefs] else 1)

        return out

    # --------------------------- Utilities --------------------------------
    def explain_recommendation(self, option: Dict[str, Any], user_id: str) -> str:
        score = float(option.get("personalization_score", 0.0))
        if score > 0.85:
            return "Perfect match for your preferences"
        if score > 0.7:
            return "Great fit based on your travel history"
        if score > 0.55:
            return "Good option that aligns with your interests"
        return "Recommended based on popularity and general fit"


def create_personalization_agent() -> PersonalizationGNN:
    return PersonalizationGNN()
