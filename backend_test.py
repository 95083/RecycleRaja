#!/usr/bin/env python3
"""
Backend API Testing for Recycle Raja E-waste Management System
Tests all backend APIs including AI-powered waste categorization
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any

# Backend URL from frontend .env
BACKEND_URL = "https://21a0b680-e972-4e7f-8153-7203cf9d753a.preview.emergentagent.com/api"

class RecycleRajaAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.created_resources = {
            'users': [],
            'waste_posts': [],
            'collectors': [],
            'matches': []
        }
    
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'response_data': response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if details:
            print(f"    Details: {details}")
        if not success and response_data:
            print(f"    Response: {response_data}")
        print()
    
    def test_api_health(self):
        """Test basic API connectivity"""
        try:
            response = self.session.get(f"{BACKEND_URL}/")
            if response.status_code == 200:
                data = response.json()
                self.log_test("API Health Check", True, f"API is responding: {data.get('message', 'OK')}")
                return True
            else:
                self.log_test("API Health Check", False, f"Status code: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("API Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def test_categories_endpoint(self):
        """Test GET /api/categories - E-waste categories"""
        try:
            response = self.session.get(f"{BACKEND_URL}/categories")
            if response.status_code == 200:
                data = response.json()
                categories = data.get('categories', [])
                if len(categories) > 0:
                    self.log_test("E-waste Categories API", True, 
                                f"Retrieved {len(categories)} categories: {', '.join(categories[:3])}...")
                    return True
                else:
                    self.log_test("E-waste Categories API", False, "No categories returned")
                    return False
            else:
                self.log_test("E-waste Categories API", False, f"Status code: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("E-waste Categories API", False, f"Error: {str(e)}")
            return False
    
    def test_create_user(self):
        """Test POST /api/users - Create user"""
        try:
            user_data = {
                "name": "Rajesh Kumar",
                "email": "rajesh.kumar@email.com",
                "phone": "+91-9876543210",
                "user_type": "waste_generator",
                "location": {"lat": 28.6139, "lng": 77.2090},
                "address": "123 Green Street, New Delhi, India"
            }
            
            response = self.session.post(f"{BACKEND_URL}/users", json=user_data)
            if response.status_code == 200:
                data = response.json()
                user_id = data.get('id')
                if user_id:
                    self.created_resources['users'].append(user_id)
                    self.log_test("Create User API", True, f"User created with ID: {user_id}")
                    return user_id
                else:
                    self.log_test("Create User API", False, "No user ID returned", data)
                    return None
            else:
                self.log_test("Create User API", False, f"Status code: {response.status_code}", response.text)
                return None
        except Exception as e:
            self.log_test("Create User API", False, f"Error: {str(e)}")
            return None
    
    def test_create_collector_user(self):
        """Test creating a collector user"""
        try:
            collector_user_data = {
                "name": "EcoRecycle Solutions",
                "email": "contact@ecorecycle.com",
                "phone": "+91-9123456789",
                "user_type": "collector",
                "location": {"lat": 28.5355, "lng": 77.3910},
                "address": "456 Industrial Area, Noida, India"
            }
            
            response = self.session.post(f"{BACKEND_URL}/users", json=collector_user_data)
            if response.status_code == 200:
                data = response.json()
                user_id = data.get('id')
                if user_id:
                    self.created_resources['users'].append(user_id)
                    self.log_test("Create Collector User API", True, f"Collector user created with ID: {user_id}")
                    return user_id
                else:
                    self.log_test("Create Collector User API", False, "No user ID returned", data)
                    return None
            else:
                self.log_test("Create Collector User API", False, f"Status code: {response.status_code}", response.text)
                return None
        except Exception as e:
            self.log_test("Create Collector User API", False, f"Error: {str(e)}")
            return None
    
    def test_ai_waste_categorization(self, user_id: str):
        """Test POST /api/waste-posts - AI-powered waste categorization (CRITICAL TEST)"""
        try:
            waste_post_data = {
                "user_id": user_id,
                "title": "Old iPhone 12 Pro Max",
                "description": "iPhone 12 Pro Max in good working condition, minor scratches on screen, battery health 85%, all functions working properly",
                "category": "Smartphones & Tablets",
                "quantity": 1,
                "weight": 0.228,
                "condition": "working",
                "images": [],
                "location": {"lat": 28.6139, "lng": 77.2090},
                "address": "123 Green Street, New Delhi, India"
            }
            
            print("Testing AI-powered waste categorization (this may take 10-15 seconds)...")
            response = self.session.post(f"{BACKEND_URL}/waste-posts", json=waste_post_data, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                post_id = data.get('id')
                ai_insights = data.get('ai_insights')
                environmental_impact = data.get('environmental_impact')
                recycling_suggestions = data.get('recycling_suggestions', [])
                price_estimate = data.get('price_estimate')
                
                if post_id:
                    self.created_resources['waste_posts'].append(post_id)
                
                # Check AI insights structure
                success = True
                details = []
                
                if ai_insights:
                    details.append("✓ AI insights generated")
                    if environmental_impact:
                        carbon_footprint = environmental_impact.get('carbon_footprint_kg')
                        toxicity_level = environmental_impact.get('toxicity_level')
                        details.append(f"✓ Environmental impact: {carbon_footprint}kg CO2, toxicity: {toxicity_level}")
                    else:
                        details.append("⚠ Environmental impact missing")
                    
                    if recycling_suggestions and len(recycling_suggestions) > 0:
                        details.append(f"✓ Recycling suggestions: {len(recycling_suggestions)} suggestions")
                    else:
                        details.append("⚠ Recycling suggestions missing")
                    
                    if price_estimate:
                        details.append(f"✓ Market value estimate: ₹{price_estimate}")
                    else:
                        details.append("⚠ Price estimate missing")
                else:
                    success = False
                    details.append("❌ AI insights not generated")
                
                self.log_test("AI-Powered Waste Categorization", success, 
                            f"Post ID: {post_id}. " + "; ".join(details), 
                            {"ai_insights": ai_insights, "environmental_impact": environmental_impact})
                return post_id if success else None
            else:
                self.log_test("AI-Powered Waste Categorization", False, 
                            f"Status code: {response.status_code}", response.text)
                return None
        except Exception as e:
            self.log_test("AI-Powered Waste Categorization", False, f"Error: {str(e)}")
            return None
    
    def test_get_waste_posts(self):
        """Test GET /api/waste-posts - Retrieve waste posts"""
        try:
            response = self.session.get(f"{BACKEND_URL}/waste-posts")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    posts_with_ai = [post for post in data if post.get('ai_insights')]
                    self.log_test("Get Waste Posts API", True, 
                                f"Retrieved {len(data)} posts, {len(posts_with_ai)} with AI insights")
                    return True
                else:
                    self.log_test("Get Waste Posts API", False, "Response is not a list", data)
                    return False
            else:
                self.log_test("Get Waste Posts API", False, f"Status code: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Get Waste Posts API", False, f"Error: {str(e)}")
            return False
    
    def test_create_collector(self, collector_user_id: str):
        """Test POST /api/collectors - Create collector profile"""
        try:
            collector_data = {
                "user_id": collector_user_id,
                "company_name": "EcoRecycle Solutions Pvt Ltd",
                "specialization": ["Smartphones & Tablets", "Laptops & Computers", "TVs & Monitors"],
                "service_radius": 25.0,
                "pricing_model": "Per item + weight based",
                "contact_info": {
                    "phone": "+91-9123456789",
                    "email": "contact@ecorecycle.com",
                    "website": "www.ecorecycle.com"
                }
            }
            
            response = self.session.post(f"{BACKEND_URL}/collectors", json=collector_data)
            if response.status_code == 200:
                data = response.json()
                collector_id = data.get('id')
                if collector_id:
                    self.created_resources['collectors'].append(collector_id)
                    self.log_test("Create Collector Profile", True, 
                                f"Collector created with ID: {collector_id}, specializes in {len(collector_data['specialization'])} categories")
                    return collector_id
                else:
                    self.log_test("Create Collector Profile", False, "No collector ID returned", data)
                    return None
            else:
                self.log_test("Create Collector Profile", False, f"Status code: {response.status_code}", response.text)
                return None
        except Exception as e:
            self.log_test("Create Collector Profile", False, f"Error: {str(e)}")
            return None
    
    def test_nearby_collectors(self):
        """Test GET /api/collectors/nearby - Location-based collector matching"""
        try:
            params = {
                "lat": 28.6139,
                "lng": 77.2090,
                "radius": 50.0,
                "category": "Smartphones & Tablets"
            }
            
            response = self.session.get(f"{BACKEND_URL}/collectors/nearby", params=params)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Nearby Collectors API", True, 
                                f"Found {len(data)} nearby collectors for smartphones category")
                    return True
                else:
                    self.log_test("Nearby Collectors API", False, "Response is not a list", data)
                    return False
            else:
                self.log_test("Nearby Collectors API", False, f"Status code: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Nearby Collectors API", False, f"Error: {str(e)}")
            return False
    
    def test_analytics_dashboard(self):
        """Test GET /api/analytics/dashboard - Environmental impact analytics"""
        try:
            response = self.session.get(f"{BACKEND_URL}/analytics/dashboard")
            if response.status_code == 200:
                data = response.json()
                required_fields = ['total_posts', 'active_posts', 'total_collectors', 'total_matches', 'environmental_impact']
                
                success = True
                details = []
                
                for field in required_fields:
                    if field in data:
                        if field == 'environmental_impact':
                            env_impact = data[field]
                            carbon_saved = env_impact.get('carbon_footprint_saved_kg', 0)
                            items_recycled = env_impact.get('items_recycled', 0)
                            details.append(f"Environmental impact: {carbon_saved}kg CO2 saved, {items_recycled} items recycled")
                        else:
                            details.append(f"{field}: {data[field]}")
                    else:
                        success = False
                        details.append(f"Missing field: {field}")
                
                self.log_test("Analytics Dashboard API", success, "; ".join(details), data)
                return success
            else:
                self.log_test("Analytics Dashboard API", False, f"Status code: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Analytics Dashboard API", False, f"Error: {str(e)}")
            return False
    
    def test_create_match(self, waste_post_id: str, collector_id: str, user_id: str):
        """Test POST /api/matches - Create collector match"""
        try:
            match_data = {
                "waste_post_id": waste_post_id,
                "collector_id": collector_id,
                "user_id": user_id,
                "estimated_price": 2500.0,
                "notes": "Quick pickup available, certified recycling process"
            }
            
            response = self.session.post(f"{BACKEND_URL}/matches", json=match_data)
            if response.status_code == 200:
                data = response.json()
                match_id = data.get('id')
                if match_id:
                    self.created_resources['matches'].append(match_id)
                    self.log_test("Create Match API", True, f"Match created with ID: {match_id}")
                    return match_id
                else:
                    self.log_test("Create Match API", False, "No match ID returned", data)
                    return None
            else:
                self.log_test("Create Match API", False, f"Status code: {response.status_code}", response.text)
                return None
        except Exception as e:
            self.log_test("Create Match API", False, f"Error: {str(e)}")
            return None
    
    def run_comprehensive_tests(self):
        """Run all backend API tests"""
        print("=" * 80)
        print("RECYCLE RAJA BACKEND API TESTING")
        print("=" * 80)
        print()
        
        # Test 1: API Health
        if not self.test_api_health():
            print("❌ API is not responding. Stopping tests.")
            return False
        
        # Test 2: Categories
        self.test_categories_endpoint()
        
        # Test 3: Create users
        user_id = self.test_create_user()
        collector_user_id = self.test_create_collector_user()
        
        if not user_id:
            print("❌ Cannot create users. Stopping dependent tests.")
            return False
        
        # Test 4: AI-powered waste categorization (CRITICAL)
        waste_post_id = self.test_ai_waste_categorization(user_id)
        
        # Test 5: Get waste posts
        self.test_get_waste_posts()
        
        # Test 6: Create collector profile
        collector_id = None
        if collector_user_id:
            collector_id = self.test_create_collector(collector_user_id)
        
        # Test 7: Nearby collectors
        self.test_nearby_collectors()
        
        # Test 8: Analytics dashboard
        self.test_analytics_dashboard()
        
        # Test 9: Create match (if we have all required IDs)
        if waste_post_id and collector_id and user_id:
            self.test_create_match(waste_post_id, collector_id, user_id)
        
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if failed_tests > 0:
            print("FAILED TESTS:")
            for test in self.test_results:
                if not test['success']:
                    print(f"❌ {test['test']}: {test['details']}")
            print()
        
        # Critical AI test result
        ai_test = next((t for t in self.test_results if 'AI-Powered' in t['test']), None)
        if ai_test:
            if ai_test['success']:
                print("🎯 CRITICAL SUCCESS: AI-powered waste categorization is working!")
            else:
                print("🚨 CRITICAL FAILURE: AI-powered waste categorization failed!")
        
        print("=" * 80)

def main():
    """Main test execution"""
    tester = RecycleRajaAPITester()
    
    try:
        tester.run_comprehensive_tests()
        tester.print_summary()
        
        # Return success status
        failed_tests = len([t for t in tester.test_results if not t['success']])
        return failed_tests == 0
        
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Test execution failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)