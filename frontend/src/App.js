import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const EWASTE_CATEGORIES = [
  "Smartphones & Tablets", "Laptops & Computers", "TVs & Monitors", 
  "Home Appliances", "Audio Equipment", "Gaming Consoles", 
  "Cables & Accessories", "Batteries", "Circuit Boards", "Other Electronics"
];

const CONDITIONS = ["working", "broken", "parts_only"];

// Hero Section Component
const HeroSection = () => {
  return (
    <div className="relative bg-gradient-to-r from-green-600 to-blue-600 text-white">
      <div className="absolute inset-0">
        <img 
          src="https://images.unsplash.com/photo-1717667745934-53091623e8ee"
          alt="Electronic waste recycling"
          className="w-full h-full object-cover opacity-30"
        />
      </div>
      <div className="relative max-w-7xl mx-auto px-4 py-24">
        <div className="text-center">
          <h1 className="text-5xl font-bold mb-6">
            Welcome to <span className="text-yellow-300">Recycle Raja</span>
          </h1>
          <p className="text-xl mb-8 max-w-3xl mx-auto">
            India's smartest AI-powered e-waste management platform. Connect with certified recyclers, 
            get instant waste categorization, and make a positive environmental impact.
          </p>
          <div className="flex justify-center space-x-4">
            <button className="bg-yellow-400 text-gray-900 px-8 py-3 rounded-lg font-semibold hover:bg-yellow-300 transition-colors">
              Post E-Waste
            </button>
            <button className="border-2 border-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-gray-900 transition-colors">
              Find Collectors
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Stats Component
const StatsSection = ({ analytics }) => {
  return (
    <div className="bg-gray-50 py-16">
      <div className="max-w-7xl mx-auto px-4">
        <h2 className="text-3xl font-bold text-center mb-12 text-gray-900">Our Impact</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="text-center">
            <div className="text-4xl font-bold text-green-600 mb-2">
              {analytics?.total_posts || 0}
            </div>
            <div className="text-gray-600">Items Posted</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-blue-600 mb-2">
              {analytics?.total_collectors || 0}
            </div>
            <div className="text-gray-600">Certified Collectors</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-purple-600 mb-2">
              {Math.round(analytics?.environmental_impact?.carbon_footprint_saved_kg || 0)}kg
            </div>
            <div className="text-gray-600">CO₂ Saved</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-orange-600 mb-2">
              {analytics?.total_matches || 0}
            </div>
            <div className="text-gray-600">Successful Matches</div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Waste Posting Form Component
const WastePostForm = ({ onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: '',
    quantity: 1,
    weight: '',
    condition: '',
    address: '',
    location: { lat: 28.6139, lng: 77.2090 } // Default Delhi
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    const postData = {
      ...formData,
      user_id: "user_1", // In real app, get from auth context
      weight: formData.weight ? parseFloat(formData.weight) : null,
      images: [] // For MVP, no image upload
    };
    
    try {
      await onSubmit(postData);
    } catch (error) {
      console.error('Error creating post:', error);
    }
    setLoading(false);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Post Your E-Waste</h2>
            <button 
              onClick={onCancel}
              className="text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Item Title *
              </label>
              <input
                type="text"
                required
                value={formData.title}
                onChange={(e) => setFormData({...formData, title: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                placeholder="e.g., iPhone 12 Pro Max"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Category *
              </label>
              <select
                required
                value={formData.category}
                onChange={(e) => setFormData({...formData, category: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="">Select category</option>
                {EWASTE_CATEGORIES.map(category => (
                  <option key={category} value={category}>{category}</option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Quantity *
                </label>
                <input
                  type="number"
                  min="1"
                  required
                  value={formData.quantity}
                  onChange={(e) => setFormData({...formData, quantity: parseInt(e.target.value)})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Weight (kg)
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={formData.weight}
                  onChange={(e) => setFormData({...formData, weight: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Condition *
                </label>
                <select
                  required
                  value={formData.condition}
                  onChange={(e) => setFormData({...formData, condition: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  <option value="">Select condition</option>
                  {CONDITIONS.map(condition => (
                    <option key={condition} value={condition}>
                      {condition.replace('_', ' ').toUpperCase()}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description *
              </label>
              <textarea
                required
                rows="4"
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                placeholder="Describe the item condition, any damages, accessories included..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Pickup Address *
              </label>
              <textarea
                required
                rows="2"
                value={formData.address}
                onChange={(e) => setFormData({...formData, address: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                placeholder="Enter your pickup address"
              />
            </div>

            <div className="flex space-x-4">
              <button
                type="button"
                onClick={onCancel}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
              >
                {loading ? "Processing..." : "Post E-Waste"}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

// Waste Post Card Component
const WastePostCard = ({ post }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-xl font-semibold text-gray-900">{post.title}</h3>
        <span className={`px-2 py-1 rounded text-xs font-medium ${
          post.status === 'active' ? 'bg-green-100 text-green-800' :
          post.status === 'matched' ? 'bg-yellow-100 text-yellow-800' :
          'bg-gray-100 text-gray-800'
        }`}>
          {post.status.toUpperCase()}
        </span>
      </div>
      
      <div className="space-y-2 mb-4">
        <p className="text-sm text-gray-600">
          <span className="font-medium">Category:</span> {post.category}
        </p>
        <p className="text-sm text-gray-600">
          <span className="font-medium">Condition:</span> {post.condition.replace('_', ' ').toUpperCase()}
        </p>
        <p className="text-sm text-gray-600">
          <span className="font-medium">Quantity:</span> {post.quantity}
          {post.weight && ` • Weight: ${post.weight}kg`}
        </p>
      </div>
      
      <p className="text-gray-700 mb-4 line-clamp-2">{post.description}</p>
      
      {post.ai_insights && (
        <div className="bg-blue-50 p-4 rounded-lg mb-4">
          <h4 className="font-semibold text-blue-900 mb-2">🤖 AI Insights</h4>
          {post.price_estimate && (
            <p className="text-sm text-blue-800 mb-2">
              <span className="font-medium">Estimated Value:</span> ₹{post.price_estimate}
            </p>
          )}
          {post.environmental_impact && (
            <p className="text-sm text-blue-800 mb-2">
              <span className="font-medium">Environmental Impact:</span> 
              {post.environmental_impact.carbon_footprint_kg}kg CO₂ equivalent
            </p>
          )}
          {post.recycling_suggestions && post.recycling_suggestions.length > 0 && (
            <div>
              <p className="text-sm font-medium text-blue-800">Recycling Tips:</p>
              <ul className="text-xs text-blue-700 ml-4">
                {post.recycling_suggestions.slice(0, 2).map((tip, idx) => (
                  <li key={idx} className="list-disc">{tip}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
      
      <div className="flex justify-between items-center">
        <p className="text-sm text-gray-500">{post.address}</p>
        <button className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
          View Details
        </button>
      </div>
    </div>
  );
};

// Main App Component
function App() {
  const [currentView, setCurrentView] = useState('home');
  const [showPostForm, setShowPostForm] = useState(false);
  const [wastePosts, setWastePosts] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchAnalytics();
    fetchWastePosts();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const response = await axios.get(`${API}/analytics/dashboard`);
      setAnalytics(response.data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    }
  };

  const fetchWastePosts = async () => {
    try {
      const response = await axios.get(`${API}/waste-posts`);
      setWastePosts(response.data);
    } catch (error) {
      console.error('Error fetching waste posts:', error);
    }
  };

  const handleCreatePost = async (postData) => {
    try {
      const response = await axios.post(`${API}/waste-posts`, postData);
      setWastePosts([response.data, ...wastePosts]);
      setShowPostForm(false);
      fetchAnalytics(); // Update stats
      alert('E-waste posted successfully! AI insights have been generated.');
    } catch (error) {
      console.error('Error creating post:', error);
      alert('Error creating post. Please try again.');
    }
  };

  const renderNavbar = () => (
    <nav className="bg-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div 
            className="flex items-center cursor-pointer"
            onClick={() => setCurrentView('home')}
          >
            <h1 className="text-2xl font-bold text-green-600">♻️ Recycle Raja</h1>
          </div>
          
          <div className="flex space-x-6">
            <button
              onClick={() => setCurrentView('home')}
              className={`px-3 py-2 rounded-md text-sm font-medium ${
                currentView === 'home' 
                  ? 'bg-green-100 text-green-700' 
                  : 'text-gray-700 hover:text-green-600'
              }`}
            >
              Home
            </button>
            <button
              onClick={() => setCurrentView('browse')}
              className={`px-3 py-2 rounded-md text-sm font-medium ${
                currentView === 'browse' 
                  ? 'bg-green-100 text-green-700' 
                  : 'text-gray-700 hover:text-green-600'
              }`}
            >
              Browse E-Waste
            </button>
            <button
              onClick={() => setCurrentView('collectors')}
              className={`px-3 py-2 rounded-md text-sm font-medium ${
                currentView === 'collectors' 
                  ? 'bg-green-100 text-green-700' 
                  : 'text-gray-700 hover:text-green-600'
              }`}
            >
              Collectors
            </button>
            <button
              onClick={() => setShowPostForm(true)}
              className="bg-green-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-green-700"
            >
              Post E-Waste
            </button>
          </div>
        </div>
      </div>
    </nav>
  );

  const renderHomePage = () => (
    <div>
      <HeroSection />
      <StatsSection analytics={analytics} />
      
      {/* Features Section */}
      <div className="py-16">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-900">
            Why Choose Recycle Raja?
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">🤖</span>
              </div>
              <h3 className="text-xl font-semibold mb-3">AI-Powered Classification</h3>
              <p className="text-gray-600">
                Get instant waste categorization, environmental impact analysis, and recycling recommendations.
              </p>
            </div>
            <div className="text-center">
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">🎯</span>
              </div>
              <h3 className="text-xl font-semibold mb-3">Smart Matching</h3>
              <p className="text-gray-600">
                Connect with certified collectors in your area who specialize in your type of e-waste.
              </p>
            </div>
            <div className="text-center">
              <div className="bg-purple-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">🌱</span>
              </div>
              <h3 className="text-xl font-semibold mb-3">Environmental Impact</h3>
              <p className="text-gray-600">
                Track your contribution to reducing carbon footprint and promoting sustainable recycling.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderBrowsePage = () => (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Browse E-Waste</h1>
        <button
          onClick={() => setShowPostForm(true)}
          className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700"
        >
          + Post E-Waste
        </button>
      </div>
      
      {wastePosts.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-600 text-lg">No e-waste posts yet. Be the first to post!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {wastePosts.map((post) => (
            <WastePostCard key={post.id} post={post} />
          ))}
        </div>
      )}
    </div>
  );

  const renderCollectorsPage = () => (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Certified Collectors</h1>
      <div className="text-center py-12">
        <p className="text-gray-600 text-lg">Collector directory coming soon!</p>
        <p className="text-gray-500 mt-2">We're onboarding certified e-waste collectors in your area.</p>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {renderNavbar()}
      
      {currentView === 'home' && renderHomePage()}
      {currentView === 'browse' && renderBrowsePage()}
      {currentView === 'collectors' && renderCollectorsPage()}
      
      {showPostForm && (
        <WastePostForm
          onSubmit={handleCreatePost}
          onCancel={() => setShowPostForm(false)}
        />
      )}
    </div>
  );
}

export default App;