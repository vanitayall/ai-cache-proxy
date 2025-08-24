import threading
import time
import torch
import json
import logging
from datetime import datetime, timedelta
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments, DataCollatorForLanguageModeling, pipeline
from datasets import Dataset
from redis_client import RedisClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LlamaTrainer:
    def __init__(self, model_id='meta-llama/Llama-3.2-1B-Instruct', redis_host='localhost', redis_port=6379, redis_db=0):
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.bfloat16,
            device_map='auto'
        )
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.redis = RedisClient(host=redis_host, port=redis_port, db=redis_db)
        logger.info("LlamaTrainer initialized successfully")

    def get_training_data(self):
        keys = self.redis.get_all_keys()
        data = []

        for key in keys:
            request_data = self.redis.get_request_data(key)
            if 'request_url' in request_data and 'response' in request_data:
                input_text = f"Request URL: {request_data['request_url']}\nResponse: {request_data['response']}"
                data.append(input_text)

        return data

    def prepare_dataset(self, data):
        dataset = Dataset.from_dict({"text": data})

        def tokenize_function(examples):
            return self.tokenizer(examples["text"], padding="max_length", truncation=True, max_length=512)

        tokenized_dataset = dataset.map(tokenize_function, batched=True)
        return tokenized_dataset

    def fine_tune_model(self, tokenized_dataset):
        training_args = TrainingArguments(
            output_dir="./llama_finetuned",
            overwrite_output_dir=True,
            num_train_epochs=3,
            per_device_train_batch_size=4,
            save_steps=10_000,
            save_total_limit=2,
            fp16=True,
            logging_dir='./logs',
        )

        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer, mlm=False
        )

        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_dataset,
            data_collator=data_collator,
        )

        trainer.train()

    def run_training(self):
        logger.info("Fetching data from Redis...")
        data = self.get_training_data()
        if not data:
            logger.info("No data to train on.")
            return

        logger.info("Preparing dataset...")
        tokenized_dataset = self.prepare_dataset(data)

        logger.info("Starting fine-tuning of LLaMA model...")
        self.fine_tune_model(tokenized_dataset)
        logger.info("Fine-tuning completed.")

    def update_cache(self, request_data):
        self.redis.store_request_data(request_data)

class LlamaModel:
    def __init__(self, model_id='meta-llama/Llama-3.2-1B-Instruct', guard_model_id="meta-llama/Llama-Guard-3-1B"):
        self.pipe = pipeline(
            'text-generation',
            model=model_id,
            torch_dtype=torch.bfloat16,
            device_map='auto'
        )
        self.guard_tokenizer = AutoTokenizer.from_pretrained(guard_model_id)
        self.guard_model = AutoModelForCausalLM.from_pretrained(
            guard_model_id,
            torch_dtype=torch.bfloat16,
            device_map="auto"
        )
        logger.info("LlamaModel initialized successfully")

    def check_inappropriate_content(self, user_input):
        input_text = f"<|user|> {user_input} "
        input_ids = self.guard_tokenizer.encode(input_text, return_tensors='pt').to(self.guard_model.device)

        with torch.no_grad():
            output_ids = self.guard_model.generate(
                input_ids,
                max_length=input_ids.size(1) + 50,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.guard_tokenizer.eos_token_id
            )

        output_text = self.guard_tokenizer.decode(output_ids[0], skip_special_tokens=True)
        response = output_text[len(input_text):].strip()

        if "no" in response.lower() or "not allowed" in response.lower():
            logger.warning("Inappropriate request detected.")
            return False

        return True

    def analyze_request(self, request_data):
        conversation = [
            {
                "role": "system",
                "content": (
                    "You are an intelligent cache management assistant. "
                    "Analyze the following request data and determine the optimal caching strategy: "
                    "1. 'delete' - if the content is outdated or irrelevant "
                    "2. 'refresh' - if the content should be refreshed soon "
                    "3. 'keep' - if the content is still valid and useful "
                    "Consider factors like request frequency, content type, and response size."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Request Method: {request_data['request_method']}\n"
                    f"Request URL: {request_data['request_url']}\n"
                    f"Request Headers: {request_data['request_headers']}\n"
                    f"Response Size: {len(request_data.get('response', ''))} bytes\n"
                    f"Request Count: {request_data.get('request_count', 0)}\n"
                    f"Last Used: {request_data.get('last_used', 'unknown')}"
                )
            }
        ]

        try:
            output = self.pipe(conversation, max_new_tokens=150)
            analysis_result = output[0]['generated_text'].strip().lower()
            logger.info(f"AI Analysis result: {analysis_result}")
        except Exception as e:
            logger.error(f"Error during model inference: {e}")
            return 'keep'

        if 'delete' in analysis_result:
            return 'delete'
        elif 'refresh' in analysis_result:
            return 'refresh'
        else:
            return 'keep'

    def predict_optimal_ttl(self, request_data):
        """Predict optimal TTL based on request patterns and content analysis"""
        conversation = [
            {
                "role": "system",
                "content": (
                    "You are a cache optimization expert. "
                    "Predict the optimal Time-to-Live (TTL) in seconds for this request. "
                    "Consider factors like content volatility, request frequency, and response size. "
                    "Return only a number between 60 and 86400 (1 minute to 24 hours)."
                )
            },
            {
                "role": "user",
                "content": (
                    f"URL: {request_data['request_url']}\n"
                    f"Method: {request_data['request_method']}\n"
                    f"Response Size: {len(request_data.get('response', ''))} bytes\n"
                    f"Request Count: {request_data.get('request_count', 0)}\n"
                    f"Content Type: {request_data.get('content_type', 'unknown')}"
                )
            }
        ]

        try:
            output = self.pipe(conversation, max_new_tokens=50)
            result = output[0]['generated_text'].strip()
            # Extract number from result
            import re
            numbers = re.findall(r'\d+', result)
            if numbers:
                ttl = int(numbers[0])
                return max(60, min(86400, ttl))  # Clamp between 60 and 86400
        except Exception as e:
            logger.error(f"Error predicting TTL: {e}")
        
        return 3600  # Default 1 hour

class RequestAnalyzer:
    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=0):
        self.redis = RedisClient(host=redis_host, port=redis_port, db=redis_db)
        self.llama = LlamaModel()
        self.analytics = AnalyticsTracker(redis_host, redis_port, redis_db)
        logger.info("RequestAnalyzer initialized successfully")

    def analyze_requests(self):
        keys = self.redis.get_all_keys()
        current_time = time.time()
        processed_count = 0
        ai_predictions = 0

        for key in keys:
            try:
                request_data = self.redis.get_request_data(key)

                if not self.llama.check_inappropriate_content(request_data['request_url']):
                    logger.warning(f"Request {key} contains inappropriate content and will be ignored.")
                    continue

                # AI-powered analysis
                action = self.llama.analyze_request(request_data)
                ai_predictions += 1

                if action == 'delete':
                    logger.info(f"Request {key} flagged for deletion.")
                    self.redis.delete_request(key)
                elif action == 'refresh':
                    logger.info(f"Request {key} marked for refreshing.")
                    self.redis.client.hset(key, "purpose", "refresh")
                else:
                    logger.info(f"Request {key} will be kept as is.")
                    self.redis.client.hset(key, "purpose", "keep")

                # TTL optimization
                request_count = self.redis.get_request_count(key)
                last_used_time = float(request_data.get('last_used', 0))
                
                if request_count == 1 and (current_time - last_used_time) > 72 * 3600:
                    optimal_ttl = self.llama.predict_optimal_ttl(request_data)
                    logger.info(f"Setting optimal TTL {optimal_ttl}s for {key}")
                    self.redis.set_ttl(key, optimal_ttl)

                if request_data["request_method"] == "POST":
                    logger.info(f"POST request detected: {key}.")
                    self.delete_old_requests(request_data["request_url"])
                    self.mark_related_get_as_refresh(request_data["request_url"])

                self.redis.increment_request_count(key)
                processed_count += 1

                # Update cache with the analyzed request data
                self.llama.update_cache(request_data)

            except Exception as e:
                logger.error(f"Error analyzing request {key}: {e}")

        # Update analytics
        self.analytics.update_ai_predictions(ai_predictions)
        logger.info(f"Processed {processed_count} requests with {ai_predictions} AI predictions")

    def delete_old_requests(self, request_url):
        all_keys = self.redis.get_all_keys()
        newest_time = None
        newest_key = None

        for key in all_keys:
            request_data = self.redis.get_request_data(key)
            if request_data["request_url"] == request_url:
                request_time = float(request_data.get('last_used', 0))
                if newest_time is None or request_time > newest_time:
                    newest_time = request_time
                    newest_key = key

        if newest_key:
            for key in all_keys:
                request_data = self.redis.get_request_data(key)
                if request_data["request_url"] == request_url:
                    request_time = float(request_data.get('last_used', 0))
                    if request_time < newest_time:
                        logger.info(f"Deleting older request {key} for URL {request_data['request_url']}")
                        self.redis.delete_request(key)

    def mark_related_get_as_refresh(self, request_url):
        all_keys = self.redis.get_all_keys()
        for key in all_keys:
            request_data = self.redis.get_request_data(key)
            if request_data["request_method"] == "GET" and self.compare_urls(request_data["request_url"], request_url):
                logger.info(f"Marking GET request {key} as 'refresh' for URL {request_data['request_url']}")
                self.redis.client.hset(key, "purpose", "refresh")

    @staticmethod
    def compare_urls(url1, url2):
        return url1.lower() == url2.lower()  

    def run(self):
        logger.info("Starting request analyzer...")
        while True:
            try:
                self.analyze_requests()
                time.sleep(600)  # Run every 10 minutes
            except Exception as e:
                logger.error(f"Error in analyzer loop: {e}")
                time.sleep(60)  # Wait 1 minute before retrying

class AnalyticsTracker:
    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=0):
        self.redis = RedisClient(host=redis_host, port=redis_port, db=redis_db)

    def update_ai_predictions(self, count):
        """Update AI predictions counter"""
        self.redis.client.incr("stats:ai_predictions", count)

    def get_performance_metrics(self):
        """Get comprehensive performance metrics"""
        try:
            total_requests = int(self.redis.client.get("stats:total_requests") or 0)
            cache_hits = int(self.redis.client.get("stats:cache_hits") or 0)
            cache_misses = int(self.redis.client.get("stats:cache_misses") or 0)
            ai_predictions = int(self.redis.client.get("stats:ai_predictions") or 0)

            cache_hit_rate = cache_hits / total_requests if total_requests > 0 else 0

            return {
                "total_requests": total_requests,
                "cache_hits": cache_hits,
                "cache_misses": cache_misses,
                "cache_hit_rate": cache_hit_rate,
                "ai_predictions": ai_predictions,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {}

# --------------- Multithreading Execution -----------------
def run_trainer():
    trainer = LlamaTrainer()
    trainer.run_training()

def run_analyzer():
    analyzer = RequestAnalyzer()
    analyzer.run()

if __name__ == "__main__":
    logger.info("Starting AI Cache Proxy LLaMA Service...")
    
    trainer_thread = threading.Thread(target=run_trainer, daemon=True)
    analyzer_thread = threading.Thread(target=run_analyzer, daemon=True)

    trainer_thread.start()
    analyzer_thread.start()

    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down LLaMA service...")
        trainer_thread.join(timeout=5)
        analyzer_thread.join(timeout=5)
        logger.info("Service shutdown complete.")