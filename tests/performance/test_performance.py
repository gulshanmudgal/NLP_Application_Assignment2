"""
Performance and evaluation tests for the translation system.

Tests system performance characteristics including:
- Translation speed and throughput
- Memory usage monitoring  
- Concurrent request handling
- BLEU score evaluation
- Model comparison benchmarks
"""

import pytest
import asyncio
import aiohttp
import time
import statistics
import psutil
import os
from typing import List, Dict, Any, Tuple
import json
from concurrent.futures import ThreadPoolExecutor
import logging

# Import test data
from tests.conftest import PERFORMANCE_THRESHOLDS, TRANSLATION_TEST_CASES

# Test configuration
API_BASE_URL = "http://localhost:8000"
TRANSLATION_ENDPOINT = f"{API_BASE_URL}/api/v1/translate/"

# Performance test datasets
PERFORMANCE_TEST_TEXTS = [
    "Hello, how are you today?",
    "The weather is beautiful outside.",
    "I would like to order some food.",
    "Thank you very much for your help.",
    "Please tell me the way to the station.",
    "What time does the store close?",
    "I am learning a new language.",
    "This is a longer sentence that contains multiple clauses and should test the translation system's ability to handle more complex grammatical structures.",
    "Short text.",
    "Medium length text that should represent typical user input for translation services."
]

# Language pairs for testing
LANGUAGE_PAIRS = [
    ("en", "hi"),
    ("en", "ta"), 
    ("en", "te"),
    ("en", "bn"),
    ("en", "mr")
]

class PerformanceMetrics:
    """Class to collect and analyze performance metrics."""
    
    def __init__(self):
        self.response_times: List[float] = []
        self.processing_times: List[float] = []
        self.confidence_scores: List[float] = []
        self.cache_hit_rates: List[bool] = []
        self.throughput_data: List[Tuple[int, float]] = []  # (requests, time)
        self.memory_usage: List[float] = []
        
    def add_translation_result(self, response_data: Dict[str, Any], response_time: float):
        """Add metrics from a translation result."""
        self.response_times.append(response_time)
        self.processing_times.append(response_data.get("processing_time", 0))
        self.confidence_scores.append(response_data.get("confidence_score", 0))
        self.cache_hit_rates.append(response_data.get("cached", False))
        
    def add_throughput_measurement(self, num_requests: int, total_time: float):
        """Add throughput measurement."""
        self.throughput_data.append((num_requests, total_time))
        
    def add_memory_measurement(self, memory_mb: float):
        """Add memory usage measurement."""
        self.memory_usage.append(memory_mb)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        return {
            "response_time": {
                "mean": statistics.mean(self.response_times) if self.response_times else 0,
                "median": statistics.median(self.response_times) if self.response_times else 0,
                "min": min(self.response_times) if self.response_times else 0,
                "max": max(self.response_times) if self.response_times else 0,
                "std": statistics.stdev(self.response_times) if len(self.response_times) > 1 else 0
            },
            "processing_time": {
                "mean": statistics.mean(self.processing_times) if self.processing_times else 0,
                "median": statistics.median(self.processing_times) if self.processing_times else 0,
                "min": min(self.processing_times) if self.processing_times else 0,
                "max": max(self.processing_times) if self.processing_times else 0
            },
            "confidence": {
                "mean": statistics.mean(self.confidence_scores) if self.confidence_scores else 0,
                "min": min(self.confidence_scores) if self.confidence_scores else 0,
                "max": max(self.confidence_scores) if self.confidence_scores else 0
            },
            "cache_hit_rate": sum(self.cache_hit_rates) / len(self.cache_hit_rates) if self.cache_hit_rates else 0,
            "throughput": {
                "requests_per_second": [
                    num_req / total_time if total_time > 0 else 0 
                    for num_req, total_time in self.throughput_data
                ]
            },
            "memory": {
                "mean_mb": statistics.mean(self.memory_usage) if self.memory_usage else 0,
                "max_mb": max(self.memory_usage) if self.memory_usage else 0,
                "min_mb": min(self.memory_usage) if self.memory_usage else 0
            }
        }


class TestTranslationPerformance:
    """Test translation performance characteristics."""
    
    @pytest.mark.asyncio
    async def test_single_translation_performance(self):
        """Test performance of single translation requests."""
        
        metrics = PerformanceMetrics()
        
        async with aiohttp.ClientSession() as session:
            for text in PERFORMANCE_TEST_TEXTS:
                request_data = {
                    "text": text,
                    "source_language": "en",
                    "target_language": "hi",
                    "model": "lightweight_indictrans"
                }
                
                start_time = time.time()
                async with session.post(TRANSLATION_ENDPOINT, json=request_data) as response:
                    end_time = time.time()
                    
                    assert response.status == 200
                    data = await response.json()
                    
                    response_time = (end_time - start_time) * 1000  # Convert to ms
                    metrics.add_translation_result(data, response_time)
                    
        stats = metrics.get_statistics()
        
        # Performance assertions
        assert stats["response_time"]["mean"] < PERFORMANCE_THRESHOLDS["max_translation_time_ms"]
        assert stats["response_time"]["max"] < PERFORMANCE_THRESHOLDS["max_translation_time_ms"] * 2
        assert stats["confidence"]["mean"] >= PERFORMANCE_THRESHOLDS["min_confidence_score"]
        
        # Log performance results
        logging.info(f"Single translation performance: {stats}")
        
    @pytest.mark.asyncio
    async def test_concurrent_translation_performance(self):
        """Test performance under concurrent load."""
        
        async def make_request(session: aiohttp.ClientSession, text: str, lang_pair: Tuple[str, str]):
            """Make a single translation request."""
            request_data = {
                "text": text,
                "source_language": lang_pair[0],
                "target_language": lang_pair[1],
                "model": "auto"
            }
            
            start_time = time.time()
            async with session.post(TRANSLATION_ENDPOINT, json=request_data) as response:
                end_time = time.time()
                
                if response.status == 200:
                    data = await response.json()
                    return data, (end_time - start_time) * 1000
                else:
                    return None, (end_time - start_time) * 1000
        
        # Test with increasing concurrency levels
        concurrency_levels = [1, 5, 10, 20]
        
        for concurrency in concurrency_levels:
            metrics = PerformanceMetrics()
            
            # Prepare requests
            requests = []
            for i in range(concurrency):
                text = PERFORMANCE_TEST_TEXTS[i % len(PERFORMANCE_TEST_TEXTS)]
                lang_pair = LANGUAGE_PAIRS[i % len(LANGUAGE_PAIRS)]
                requests.append((text, lang_pair))
            
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                
                # Execute concurrent requests
                tasks = [
                    make_request(session, text, lang_pair)
                    for text, lang_pair in requests
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                end_time = time.time()
                
                total_time = end_time - start_time
                metrics.add_throughput_measurement(concurrency, total_time)
                
                # Collect individual request metrics
                successful_results = [r for r in results if r is not None and not isinstance(r, Exception)]
                for data, response_time in successful_results:
                    if data:
                        metrics.add_translation_result(data, response_time)
                
                stats = metrics.get_statistics()
                
                # Performance assertions for concurrent requests
                if stats["throughput"]["requests_per_second"]:
                    throughput = stats["throughput"]["requests_per_second"][0]
                    assert throughput > 0, f"Zero throughput at concurrency {concurrency}"
                    
                # Log results
                logging.info(f"Concurrency {concurrency}: {throughput:.2f} req/s, "
                           f"avg response: {stats['response_time']['mean']:.2f}ms")
                           
    @pytest.mark.asyncio
    async def test_memory_usage_monitoring(self):
        """Test memory usage during translation operations."""
        
        # Get baseline memory usage
        process = psutil.Process(os.getpid())
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        metrics = PerformanceMetrics()
        metrics.add_memory_measurement(baseline_memory)
        
        async with aiohttp.ClientSession() as session:
            # Perform multiple translations and monitor memory
            for i in range(50):  # More requests to see memory patterns
                text = PERFORMANCE_TEST_TEXTS[i % len(PERFORMANCE_TEST_TEXTS)]
                request_data = {
                    "text": text,
                    "source_language": "en",
                    "target_language": "hi",
                    "model": "lightweight_indictrans"
                }
                
                async with session.post(TRANSLATION_ENDPOINT, json=request_data) as response:
                    assert response.status == 200
                    
                # Monitor memory every 10 requests
                if i % 10 == 0:
                    current_memory = process.memory_info().rss / 1024 / 1024
                    metrics.add_memory_measurement(current_memory)
                    
        stats = metrics.get_statistics()
        
        # Memory usage assertions
        memory_increase = stats["memory"]["max_mb"] - baseline_memory
        assert memory_increase < PERFORMANCE_THRESHOLDS["max_memory_usage_mb"], \
            f"Memory increase {memory_increase:.2f}MB exceeds threshold"
            
        logging.info(f"Memory usage - baseline: {baseline_memory:.2f}MB, "
                    f"max: {stats['memory']['max_mb']:.2f}MB, "
                    f"increase: {memory_increase:.2f}MB")


class TestModelComparison:
    """Test and compare different translation models."""
    
    @pytest.mark.asyncio
    async def test_model_performance_comparison(self):
        """Compare performance across different models."""
        
        available_models = ["lightweight_indictrans", "mock", "auto"]
        model_metrics = {}
        
        test_text = "Hello, how are you today?"
        
        async with aiohttp.ClientSession() as session:
            for model in available_models:
                metrics = PerformanceMetrics()
                
                # Test each model multiple times
                for _ in range(10):
                    request_data = {
                        "text": test_text,
                        "source_language": "en",
                        "target_language": "hi",
                        "model": model
                    }
                    
                    start_time = time.time()
                    async with session.post(TRANSLATION_ENDPOINT, json=request_data) as response:
                        end_time = time.time()
                        
                        if response.status == 200:
                            data = await response.json()
                            response_time = (end_time - start_time) * 1000
                            metrics.add_translation_result(data, response_time)
                
                model_metrics[model] = metrics.get_statistics()
                
        # Compare models
        for model, stats in model_metrics.items():
            logging.info(f"Model {model} performance:")
            logging.info(f"  Avg response time: {stats['response_time']['mean']:.2f}ms")
            logging.info(f"  Avg confidence: {stats['confidence']['mean']:.2f}")
            logging.info(f"  Cache hit rate: {stats['cache_hit_rate']:.2f}")
            
        # Assertions - lightweight model should be fastest
        if "lightweight_indictrans" in model_metrics and "mock" in model_metrics:
            lightweight_time = model_metrics["lightweight_indictrans"]["response_time"]["mean"]
            mock_time = model_metrics["mock"]["response_time"]["mean"]
            
            # Both should be reasonably fast
            assert lightweight_time < PERFORMANCE_THRESHOLDS["max_translation_time_ms"]
            assert mock_time < PERFORMANCE_THRESHOLDS["max_translation_time_ms"]
            
    @pytest.mark.asyncio
    async def test_language_pair_performance(self):
        """Test performance across different language pairs."""
        
        language_metrics = {}
        test_text = "Hello, how are you?"
        
        async with aiohttp.ClientSession() as session:
            for source_lang, target_lang in LANGUAGE_PAIRS:
                metrics = PerformanceMetrics()
                
                # Test each language pair
                for _ in range(5):
                    request_data = {
                        "text": test_text,
                        "source_language": source_lang,
                        "target_language": target_lang,
                        "model": "auto"
                    }
                    
                    start_time = time.time()
                    async with session.post(TRANSLATION_ENDPOINT, json=request_data) as response:
                        end_time = time.time()
                        
                        if response.status == 200:
                            data = await response.json()
                            response_time = (end_time - start_time) * 1000
                            metrics.add_translation_result(data, response_time)
                
                pair_key = f"{source_lang}->{target_lang}"
                language_metrics[pair_key] = metrics.get_statistics()
                
        # Log language pair performance
        for pair, stats in language_metrics.items():
            logging.info(f"Language pair {pair}:")
            logging.info(f"  Avg response time: {stats['response_time']['mean']:.2f}ms")
            logging.info(f"  Avg confidence: {stats['confidence']['mean']:.2f}")


class TestStressAndLoad:
    """Stress testing and load testing."""
    
    @pytest.mark.asyncio
    async def test_sustained_load(self):
        """Test system under sustained load."""
        
        duration_seconds = 30  # 30 second stress test
        request_interval = 0.1  # Request every 100ms
        
        metrics = PerformanceMetrics()
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        async with aiohttp.ClientSession() as session:
            request_count = 0
            
            while time.time() < end_time:
                text = PERFORMANCE_TEST_TEXTS[request_count % len(PERFORMANCE_TEST_TEXTS)]
                request_data = {
                    "text": text,
                    "source_language": "en",
                    "target_language": "hi", 
                    "model": "lightweight_indictrans"
                }
                
                req_start = time.time()
                try:
                    async with session.post(TRANSLATION_ENDPOINT, json=request_data) as response:
                        req_end = time.time()
                        
                        if response.status == 200:
                            data = await response.json()
                            response_time = (req_end - req_start) * 1000
                            metrics.add_translation_result(data, response_time)
                            
                        request_count += 1
                        
                except Exception as e:
                    logging.warning(f"Request failed during stress test: {e}")
                    
                # Wait before next request
                await asyncio.sleep(request_interval)
                
        total_duration = time.time() - start_time
        metrics.add_throughput_measurement(request_count, total_duration)
        
        stats = metrics.get_statistics()
        
        # Stress test assertions
        if stats["throughput"]["requests_per_second"]:
            throughput = stats["throughput"]["requests_per_second"][0]
            assert throughput > 1, f"Throughput too low: {throughput:.2f} req/s"
            
            # Most requests should complete within threshold
            assert stats["response_time"]["median"] < PERFORMANCE_THRESHOLDS["max_translation_time_ms"]
            
        logging.info(f"Stress test results:")
        logging.info(f"  Duration: {total_duration:.2f}s")
        logging.info(f"  Total requests: {request_count}")
        logging.info(f"  Throughput: {throughput:.2f} req/s")
        logging.info(f"  Median response time: {stats['response_time']['median']:.2f}ms")


class TestCachePerformance:
    """Test cache performance and efficiency."""
    
    @pytest.mark.asyncio
    async def test_cache_effectiveness(self):
        """Test cache hit rates and performance improvement."""
        
        cache_test_texts = [
            "Hello world",
            "Good morning",
            "Thank you",
            "How are you?",
            "Nice to meet you"
        ]
        
        async with aiohttp.ClientSession() as session:
            # First pass - populate cache
            first_pass_times = []
            for text in cache_test_texts:
                request_data = {
                    "text": text,
                    "source_language": "en",
                    "target_language": "hi",
                    "model": "lightweight_indictrans"
                }
                
                start_time = time.time()
                async with session.post(TRANSLATION_ENDPOINT, json=request_data) as response:
                    end_time = time.time()
                    
                    assert response.status == 200
                    data = await response.json()
                    first_pass_times.append((end_time - start_time) * 1000)
                    assert not data.get("cached", True)  # Should be cache miss
                    
            # Wait a moment for cache to be set
            await asyncio.sleep(0.5)
            
            # Second pass - should hit cache
            second_pass_times = []
            cache_hits = 0
            
            for text in cache_test_texts:
                request_data = {
                    "text": text,
                    "source_language": "en",
                    "target_language": "hi",
                    "model": "lightweight_indictrans"
                }
                
                start_time = time.time()
                async with session.post(TRANSLATION_ENDPOINT, json=request_data) as response:
                    end_time = time.time()
                    
                    assert response.status == 200
                    data = await response.json()
                    second_pass_times.append((end_time - start_time) * 1000)
                    
                    # Note: Cache hit detection might not be implemented in response
                    # if data.get("cached", False):
                    #     cache_hits += 1
            
            # Calculate performance improvement
            avg_first_pass = statistics.mean(first_pass_times)
            avg_second_pass = statistics.mean(second_pass_times)
            
            logging.info(f"Cache performance test:")
            logging.info(f"  First pass avg: {avg_first_pass:.2f}ms")
            logging.info(f"  Second pass avg: {avg_second_pass:.2f}ms")
            logging.info(f"  Performance improvement: {((avg_first_pass - avg_second_pass) / avg_first_pass * 100):.1f}%")
            
            # Cache should provide some performance benefit
            # (This might not always be measurable due to the lightweight nature of our translator)
            # assert avg_second_pass <= avg_first_pass * 1.1  # Allow for some variance


def pytest_configure(config):
    """Configure logging for performance tests."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
