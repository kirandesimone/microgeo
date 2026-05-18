"""Pydantic models for API requests and responses."""
 
from typing import Any, Optional
 
from pydantic import BaseModel, Field
 
 
# Geometry primitives
 
class Point(BaseModel):
    """A single point in WGS84 (EPSG:4326)."""
 
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lon: float = Field(..., ge=-180, le=180, description="Longitude")
 
 
class BoundingBox(BaseModel):
    """Axis-aligned bounding box in WGS84 (EPSG:4326)."""
 
    min_lat: float = Field(..., ge=-90, le=90, description="Southern edge")
    min_lon: float = Field(..., ge=-180, le=180, description="Western edge")
    max_lat: float = Field(..., ge=-90, le=90, description="Northern edge")
    max_lon: float = Field(..., ge=-180, le=180, description="Eastern edge")
 
 
# Common responses
 
class OSMFeature(BaseModel):
    """A single OSM element, normalized to GeoJSON-ish shape."""
 
    id: str
    type: str = Field(..., description="OSM element type: node, way, relation")
    geometry: Optional[dict[str, Any]] = None
    properties: dict[str, Any] = Field(default_factory=dict)
 
 
class FeatureCollection(BaseModel):
    """GeoJSON-style collection returned by area and point queries"""
 
    type: str = "FeatureCollection"
    features: list[OSMFeature] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
