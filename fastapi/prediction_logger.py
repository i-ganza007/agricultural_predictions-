from dotenv import load_dotenv
import os
from pymongo import MongoClient
from datetime import datetime
from typing import Dict, Any
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class PredictionLogger:
    def __init__(self):
        try:
            mongo_url = os.getenv('MONGO_URL')
            if not mongo_url:
                logger.warning("MONGO_URL not found in environment variables")
                self.client = None
                self.db = None
                self.predictions_collection = None
                return
                
            self.client = MongoClient(mongo_url)
            # Test the connection
            self.client.admin.command('ismaster')
            self.db = self.client['agri-yield']
            self.predictions_collection = self.db.predictions
            logger.info("MongoDB connection established for prediction logging")
        except Exception as e:
            logger.warning(f"Failed to connect to MongoDB: {e}")
            self.client = None
            self.db = None
            self.predictions_collection = None
    
    def log_prediction(self, prediction_data: Dict[str, Any]) -> bool:
        """Log prediction to MongoDB"""
        if self.predictions_collection is None:
            return False
        
        try:
            log_entry = {
                **prediction_data,
                "timestamp": datetime.utcnow(),
                "prediction_type": prediction_data.get("model_used", "unknown")
            }
            
            result = self.predictions_collection.insert_one(log_entry)
            logger.info(f"Prediction logged with ID: {result.inserted_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log prediction: {e}")
            return False
    
    def get_prediction_history(self, area_id: int = None, item_id: int = None, limit: int = 100):
        """Retrieve prediction history from MongoDB"""
        if self.predictions_collection is None:
            return []
        
        try:
            query = {}
            if area_id:
                query["area_id"] = area_id
            if item_id:
                query["item_id"] = item_id
            
            predictions = list(
                self.predictions_collection
                .find(query, {"_id": 0})
                .sort("timestamp", -1)
                .limit(limit)
            )
            return predictions
            
        except Exception as e:
            logger.error(f"Failed to retrieve prediction history: {e}")
            return []
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()

# Global instance
prediction_logger = PredictionLogger()
