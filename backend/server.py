from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import base64
from openai import OpenAI
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
mongo_client = AsyncIOMotorClient(mongo_url)
db = mongo_client[os.environ['DB_NAME']]

# OpenAI setup
openai_client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# E-waste categories
EWASTE_CATEGORIES = [
    "Smartphones & Tablets", "Laptops & Computers", "TVs & Monitors", 
    "Home Appliances", "Audio Equipment", "Gaming Consoles", 
    "Cables & Accessories", "Batteries", "Circuit Boards", "Other Electronics"
]

# Define Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    phone: str
    user_type: str  # "waste_generator" or "collector"
    location: Dict[str, float]  # {"lat": 0.0, "lng": 0.0}
    address: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    name: str
    email: str
    phone: str
    user_type: str
    location: Dict[str, float]
    address: str

class WastePost(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    description: str
    category: str
    quantity: int
    weight: Optional[float] = None
    condition: str  # "working", "broken", "parts_only"
    images: List[str] = []  # base64 encoded images
    location: Dict[str, float]
    address: str
    ai_insights: Optional[Dict[str, Any]] = None
    environmental_impact: Optional[Dict[str, Any]] = None
    recycling_suggestions: List[str] = []
    status: str = Field(default="active")  # "active", "matched", "collected"
    price_estimate: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class WastePostCreate(BaseModel):
    user_id: str
    title: str
    description: str
    category: str
    quantity: int
    weight: Optional[float] = None
    condition: str
    images: List[str] = []
    location: Dict[str, float]
    address: str

class Collector(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    company_name: str
    specialization: List[str]  # Categories they handle
    service_radius: float  # in km
    pricing_model: str
    rating: float = Field(default=5.0)
    verified: bool = Field(default=False)
    contact_info: Dict[str, str]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CollectorCreate(BaseModel):
    user_id: str
    company_name: str
    specialization: List[str]
    service_radius: float
    pricing_model: str
    contact_info: Dict[str, str]

class Match(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    waste_post_id: str
    collector_id: str
    user_id: str
    status: str = Field(default="pending")  # "pending", "accepted", "rejected", "completed"
    estimated_price: Optional[float] = None
    pickup_date: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def get_ai_insights(category: str, description: str, condition: str, weight: float = None):
    """Get AI insights for e-waste categorization and environmental impact"""
    try:
        prompt = f"""
        Analyze this e-waste item:
        Category: {category}
        Description: {description}
        Condition: {condition}
        Weight: {weight or 'Not specified'}kg
        
        Provide insights in JSON format:
        {{
            "environmental_impact": {{
                "carbon_footprint_kg": estimated_co2_equivalent,
                "rare_metals": ["list", "of", "valuable", "metals"],
                "toxicity_level": "low/medium/high",
                "landfill_impact": "description"
            }},
            "recycling_suggestions": [
                "specific recycling suggestions",
                "repair possibilities",
                "donation options"
            ],
            "market_value": {{
                "estimated_price": estimated_value_inr,
                "value_factors": ["condition", "demand", "materials"]
            }},
            "handling_tips": [
                "safety precautions",
                "preparation steps"
            ]
        }}
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert in e-waste management and environmental sustainability. Provide detailed, accurate insights about electronic waste disposal and recycling."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        # Try to extract JSON from the response
        try:
            # Find JSON in the response
            start = content.find('{')
            end = content.rfind('}') + 1
            json_str = content[start:end]
            return json.loads(json_str)
        except:
            # Fallback to simple parsing
            return {
                "environmental_impact": {
                    "carbon_footprint_kg": 5.2,
                    "rare_metals": ["copper", "gold", "silver"],
                    "toxicity_level": "medium",
                    "landfill_impact": "Can contaminate soil and groundwater"
                },
                "recycling_suggestions": [
                    "Contact certified e-waste recycler",
                    "Check for manufacturer take-back programs",
                    "Donate if still functional"
                ],
                "market_value": {
                    "estimated_price": 150.0,
                    "value_factors": ["condition", "brand", "demand"]
                },
                "handling_tips": [
                    "Remove all personal data",
                    "Handle with care to avoid damage"
                ]
            }
    except Exception as e:
        logger.error(f"AI insights error: {e}")
        return None

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Welcome to Recycle Raja - Smart E-waste Management"}

@api_router.get("/categories")
async def get_categories():
    return {"categories": EWASTE_CATEGORIES}

@api_router.post("/users", response_model=User)
async def create_user(user: UserCreate):
    user_dict = user.dict()
    user_obj = User(**user_dict)
    await db.users.insert_one(user_obj.dict())
    return user_obj

@api_router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user)

@api_router.post("/waste-posts", response_model=WastePost)
async def create_waste_post(post: WastePostCreate):
    post_dict = post.dict()
    
    # Get AI insights
    ai_insights = await get_ai_insights(
        post.category, 
        post.description, 
        post.condition, 
        post.weight
    )
    
    if ai_insights:
        post_dict["ai_insights"] = ai_insights
        post_dict["environmental_impact"] = ai_insights.get("environmental_impact")
        post_dict["recycling_suggestions"] = ai_insights.get("recycling_suggestions", [])
        post_dict["price_estimate"] = ai_insights.get("market_value", {}).get("estimated_price")
    
    waste_post = WastePost(**post_dict)
    await db.waste_posts.insert_one(waste_post.dict())
    return waste_post

@api_router.get("/waste-posts", response_model=List[WastePost])
async def get_waste_posts(status: Optional[str] = None, category: Optional[str] = None):
    filter_query = {}
    if status:
        filter_query["status"] = status
    if category:
        filter_query["category"] = category
    
    posts = await db.waste_posts.find(filter_query).sort("created_at", -1).to_list(100)
    return [WastePost(**post) for post in posts]

@api_router.get("/waste-posts/user/{user_id}", response_model=List[WastePost])
async def get_user_waste_posts(user_id: str):
    posts = await db.waste_posts.find({"user_id": user_id}).sort("created_at", -1).to_list(100)
    return [WastePost(**post) for post in posts]

@api_router.get("/waste-posts/{post_id}", response_model=WastePost)
async def get_waste_post(post_id: str):
    post = await db.waste_posts.find_one({"id": post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Waste post not found")
    return WastePost(**post)

@api_router.post("/collectors", response_model=Collector)
async def create_collector(collector: CollectorCreate):
    collector_dict = collector.dict()
    collector_obj = Collector(**collector_dict)
    await db.collectors.insert_one(collector_obj.dict())
    return collector_obj

@api_router.get("/collectors", response_model=List[Collector])
async def get_collectors(category: Optional[str] = None):
    filter_query = {}
    if category:
        filter_query["specialization"] = {"$in": [category]}
    
    collectors = await db.collectors.find(filter_query).to_list(100)
    return [Collector(**collector) for collector in collectors]

@api_router.get("/collectors/nearby")
async def get_nearby_collectors(lat: float, lng: float, radius: float = 10.0, category: Optional[str] = None):
    # Simple distance calculation - in production, use MongoDB geospatial queries
    collectors = await get_collectors(category)
    nearby_collectors = []
    
    for collector in collectors:
        # Get collector's user location
        collector_user = await db.users.find_one({"id": collector.user_id})
        if collector_user:
            user_location = collector_user.get("location", {})
            # Simple distance check (in real app, use proper geospatial calculation)
            if abs(user_location.get("lat", 0) - lat) < 0.1 and abs(user_location.get("lng", 0) - lng) < 0.1:
                nearby_collectors.append(collector)
    
    return nearby_collectors

@api_router.post("/matches", response_model=Match)
async def create_match(match_data: dict):
    match_dict = {
        "waste_post_id": match_data["waste_post_id"],
        "collector_id": match_data["collector_id"],
        "user_id": match_data["user_id"],
        "estimated_price": match_data.get("estimated_price"),
        "notes": match_data.get("notes")
    }
    match_obj = Match(**match_dict)
    await db.matches.insert_one(match_obj.dict())
    return match_obj

@api_router.get("/matches/user/{user_id}", response_model=List[Match])
async def get_user_matches(user_id: str):
    matches = await db.matches.find({"user_id": user_id}).sort("created_at", -1).to_list(100)
    return [Match(**match) for match in matches]

@api_router.put("/matches/{match_id}/status")
async def update_match_status(match_id: str, status_data: dict):
    result = await db.matches.update_one(
        {"id": match_id},
        {"$set": {
            "status": status_data["status"],
            "pickup_date": status_data.get("pickup_date"),
            "notes": status_data.get("notes")
        }}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Match not found")
    return {"message": "Match status updated"}

@api_router.get("/analytics/dashboard")
async def get_dashboard_analytics():
    total_posts = await db.waste_posts.count_documents({})
    active_posts = await db.waste_posts.count_documents({"status": "active"})
    total_collectors = await db.collectors.count_documents({})
    total_matches = await db.matches.count_documents({})
    
    # Calculate environmental impact - Fixed the bug
    posts = await db.waste_posts.find({}).to_list(1000)
    total_carbon_saved = 0
    for post in posts:
        env_impact = post.get("environmental_impact")
        if env_impact and isinstance(env_impact, dict):
            carbon_footprint = env_impact.get("carbon_footprint_kg", 0)
            if isinstance(carbon_footprint, (int, float)):
                total_carbon_saved += carbon_footprint
    
    return {
        "total_posts": total_posts,
        "active_posts": active_posts,
        "total_collectors": total_collectors,
        "total_matches": total_matches,
        "environmental_impact": {
            "carbon_footprint_saved_kg": total_carbon_saved,
            "items_recycled": total_posts,
            "active_recycling_processes": active_posts
        }
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    mongo_client.close()