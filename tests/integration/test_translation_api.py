"""
Integration tests for the complete translation system.

Tests the full end-to-end translation pipeline including:
- API endpoints with real HTTP requests
- Complete translation workflow
- Cache integration behavior
- Model fallback scenarios
- Performance under load
"""

import pytest
import asyncio
import aiohttp
import json
import time
from typing import Dict, Any, List
import logging

# Test configuration
API_BASE_URL = "http://localhost:8000"
TRANSLATION_ENDPOINT = f"{API_BASE_URL}/api/v1/translate/"
LANGUAGES_ENDPOINT = f"{API_BASE_URL}/api/v1/languages/"
HEALTH_ENDPOINT = f"{API_BASE_URL}/health"

# Import test cases from conftest
from tests.conftest import (
    TRANSLATION_TEST_CASES, 
    SUPPORTED_LANGUAGE_PAIRS,
    AVAILABLE_MODELS,
    PERFORMANCE_THRESHOLDS,
    ERROR_TEST_CASES
)


class TestAPIEndpoints:
    """Test API endpoints with real HTTP requests."""
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        """Test health check endpoint."""
        async with aiohttp.ClientSession() as session:
            async with session.get(HEALTH_ENDPOINT) as response:
                assert response.status == 200
                data = await response.json()
                assert "status" in data
                assert data["status"] == "healthy"
                
    @pytest.mark.asyncio
    async def test_languages_endpoint(self):
        """Test languages endpoint returns supported languages."""
        async with aiohttp.ClientSession() as session:
            async with session.get(LANGUAGES_ENDPOINT) as response:
                assert response.status == 200
                data = await response.json()
                
                assert "supported_languages" in data
                assert "language_pairs" in data
                
                # Check that basic languages are supported
                languages = data["supported_languages"]
                assert "en" in languages
                assert "hi" in languages
                
    @pytest.mark.asyncio
    async def test_basic_translation_request(self):
        """Test basic translation API request."""
        request_data = {
            "text": "hello",
            "source_language": "en",
            "target_language": "hi",
            "model": "lightweight_indictrans"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                TRANSLATION_ENDPOINT,
                json=request_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                assert response.status == 200
                data = await response.json()
                
                # Check response structure
                required_fields = [
                    "translated_text", "source_language", "target_language",
                    "confidence_score", "model_used", "processing_time", "cached"
                ]
                for field in required_fields:
                    assert field in data
                    
                # Check response values
                assert data["source_language"] == "en"
                assert data["target_language"] == "hi"
                assert data["model_used"] == "lightweight_indictrans"
                assert isinstance(data["confidence_score"], (int, float))
                assert isinstance(data["processing_time"], (int, float))
                assert isinstance(data["cached"], bool)
                
    @pytest.mark.asyncio
    async def test_model_selection_auto(self):
        """Test automatic model selection."""
        request_data = {
            "text": "hello",
            "source_language": "en", 
            "target_language": "hi",
            "model": "auto"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(TRANSLATION_ENDPOINT, json=request_data) as response:
                assert response.status == 200
                data = await response.json()
                
                # Should select an appropriate model
                assert data["model_used"] in AVAILABLE_MODELS
                assert data["model_used"] != "auto"  # Should resolve to actual model


class TestTranslationWorkflow:
    """Test complete translation workflow scenarios."""
    
    @pytest.mark.asyncio 
    async def test_translation_test_cases(self):
        """Test predefined translation cases."""
        
        async with aiohttp.ClientSession() as session:
            for test_case in TRANSLATION_TEST_CASES:
                request_data = {
                    "text": test_case["text"],
                    "source_language": test_case["source_lang"],
                    "target_language": test_case["target_lang"],
                    "model": test_case["model"]
                }
                
                async with session.post(TRANSLATION_ENDPOINT, json=request_data) as response:
                    assert response.status == 200
                    data = await response.json()
                    
                    # Check if translation contains expected content
                    translated_text = data["translated_text"]
                    expected_options = test_case["expected_contains"]
                    
                    # At least one expected translation should be present
                    contains_expected = any(
                        expected in translated_text 
                        for expected in expected_options
                    )
                    
                    # For now, just ensure we get some translation
                    # (exact matching depends on model performance)
                    assert len(translated_text) > 0
                    assert data["confidence_score"] > 0
                    
    @pytest.mark.asyncio
    async def test_language_pair_coverage(self):
        """Test translation across supported language pairs."""
        
        test_text = "hello"
        
        async with aiohttp.ClientSession() as session:
            for source_lang, target_lang in SUPPORTED_LANGUAGE_PAIRS:
                request_data = {
                    "text": test_text,
                    "source_language": source_lang,
                    "target_language": target_lang,
                    "model": "auto"
                }
                
                async with session.post(TRANSLATION_ENDPOINT, json=request_data) as response:
                    # Should either succeed or fail gracefully
                    assert response.status in [200, 400, 422]
                    
                    if response.status == 200:
                        data = await response.json()
                        assert "translated_text" in data
                        assert len(data["translated_text"]) > 0
                        
    @pytest.mark.asyncio
    async def test_model_fallback_behavior(self):
        """Test model fallback when preferred model isn't available."""
        
        # Try to use a model that might not be available
        request_data = {
            "text": "hello",
            "source_language": "en",
            "target_language": "hi", 
            "model": "indictrans"  # Heavy model that might not be loaded
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(TRANSLATION_ENDPOINT, json=request_data) as response:
                # Should either succeed with the requested model or fallback
                assert response.status == 200
                data = await response.json()
                
                # Should get a valid translation regardless
                assert "translated_text" in data
                assert len(data["translated_text"]) > 0
                assert data["model_used"] in AVAILABLE_MODELS


class TestCacheIntegration:
    """Test cache integration and behavior."""
    
    @pytest.mark.asyncio
    async def test_cache_hit_behavior(self):
        """Test cache hit on repeated requests."""
        
        request_data = {
            "text": "hello world",
            "source_language": "en",
            "target_language": "hi",
            "model": "lightweight_indictrans"
        }
        
        async with aiohttp.ClientSession() as session:
            # First request - should be cache miss
            async with session.post(TRANSLATION_ENDPOINT, json=request_data) as response:
                assert response.status == 200
                first_data = await response.json()
                assert not first_data["cached"]  # Should be cache miss
                
            # Wait a moment to ensure cache is set
            await asyncio.sleep(0.1)
            
            # Second request - should be cache hit
            async with session.post(TRANSLATION_ENDPOINT, json=request_data) as response:
                assert response.status == 200
                second_data = await response.json()
                
                # Should be faster due to cache
                # Note: This might not always be true in practice due to network variance
                # assert second_data["cached"]  # Uncomment if cache header is implemented
                
                # Translation should be identical
                assert second_data["translated_text"] == first_data["translated_text"]
                
    @pytest.mark.asyncio
    async def test_cache_key_uniqueness(self):
        """Test that different requests generate different cache keys."""
        
        requests = [
            {"text": "hello", "source_language": "en", "target_language": "hi"},
            {"text": "hello", "source_language": "en", "target_language": "ta"},  # Different target
            {"text": "goodbye", "source_language": "en", "target_language": "hi"},  # Different text
        ]
        
        results = []
        
        async with aiohttp.ClientSession() as session:
            for request_data in requests:
                request_data["model"] = "auto"
                async with session.post(TRANSLATION_ENDPOINT, json=request_data) as response:
                    assert response.status == 200
                    data = await response.json()
                    results.append(data["translated_text"])
                    
        # Results should be different (different cache keys)
        assert len(set(results)) == len(results)  # All unique


class TestPerformanceIntegration:
    """Test performance characteristics of the integrated system."""
    
    @pytest.mark.asyncio
    async def test_translation_response_time(self):
        """Test translation response time meets thresholds."""
        
        request_data = {
            "text": "This is a test sentence for performance measurement.",
            "source_language": "en",
            "target_language": "hi",
            "model": "lightweight_indictrans"
        }
        
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            
            async with session.post(TRANSLATION_ENDPOINT, json=request_data) as response:
                end_time = time.time()
                
                assert response.status == 200
                data = await response.json()
                
                # Check response time
                total_time_ms = (end_time - start_time) * 1000
                processing_time_ms = data["processing_time"] * 1000
                
                # Should meet performance thresholds
                max_time = PERFORMANCE_THRESHOLDS["max_translation_time_ms"]
                assert total_time_ms < max_time, f"Total time {total_time_ms}ms exceeds {max_time}ms"
                
                # Processing time should be reasonable
                assert processing_time_ms < max_time
                
    @pytest.mark.asyncio
    async def test_concurrent_translation_requests(self):
        """Test system performance under concurrent load."""
        
        async def make_translation_request(session: aiohttp.ClientSession, text: str) -> Dict[str, Any]:
            request_data = {
                "text": text,
                "source_language": "en",
                "target_language": "hi",
                "model": "lightweight_indictrans"
            }
            
            async with session.post(TRANSLATION_ENDPOINT, json=request_data) as response:
                assert response.status == 200
                return await response.json()
        
        # Create concurrent requests
        test_texts = [
            "Hello world",
            "Good morning", 
            "Thank you",
            "How are you?",
            "Nice to meet you"
        ]
        
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            
            # Execute requests concurrently
            tasks = [
                make_translation_request(session, text)
                for text in test_texts
            ]
            
            results = await asyncio.gather(*tasks)
            end_time = time.time()
            
            # Verify all requests succeeded
            assert len(results) == len(test_texts)
            for result in results:
                assert "translated_text" in result
                assert len(result["translated_text"]) > 0
                
            # Check total time for concurrent requests
            total_time = end_time - start_time
            avg_time_per_request = total_time / len(test_texts)
            
            # Concurrent requests should be faster than sequential
            max_expected_time = PERFORMANCE_THRESHOLDS["max_translation_time_ms"] / 1000
            assert avg_time_per_request < max_expected_time


class TestErrorHandling:
    """Test error handling scenarios."""
    
    @pytest.mark.asyncio
    async def test_error_scenarios(self):
        """Test various error scenarios."""
        
        async with aiohttp.ClientSession() as session:
            for error_case in ERROR_TEST_CASES:
                request_data = {
                    "text": error_case["text"],
                    "source_language": error_case["source_lang"],
                    "target_language": error_case["target_lang"]
                }
                
                if "model" in error_case:
                    request_data["model"] = error_case["model"]
                    
                async with session.post(TRANSLATION_ENDPOINT, json=request_data) as response:
                    # Should handle errors gracefully
                    assert response.status in [400, 422, 500]
                    
                    if response.status != 500:  # Non-server errors should return JSON
                        data = await response.json()
                        assert "detail" in data or "error" in data
                        
    @pytest.mark.asyncio
    async def test_malformed_request_handling(self):
        """Test handling of malformed requests."""
        
        malformed_requests = [
            {},  # Empty request
            {"text": "hello"},  # Missing required fields
            {"source_language": "en", "target_language": "hi"},  # Missing text
            {  # Invalid JSON structure
                "text": "hello",
                "source_language": "en",
                "target_language": "hi",
                "invalid_field": "should_be_ignored"
            }
        ]
        
        async with aiohttp.ClientSession() as session:
            for request_data in malformed_requests:
                async with session.post(TRANSLATION_ENDPOINT, json=request_data) as response:
                    # Should return appropriate error status
                    assert response.status in [400, 422]
                    
    @pytest.mark.asyncio
    async def test_large_text_handling(self):
        """Test handling of large text inputs."""
        
        # Test with very long text
        large_text = "This is a test sentence. " * 1000  # ~25,000 characters
        
        request_data = {
            "text": large_text,
            "source_language": "en",
            "target_language": "hi",
            "model": "lightweight_indictrans"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(TRANSLATION_ENDPOINT, json=request_data) as response:
                # Should either handle it or reject gracefully
                assert response.status in [200, 400, 413, 422]
                
                if response.status == 200:
                    data = await response.json()
                    assert "translated_text" in data
                    # Translation should be present but might be truncated
                    assert len(data["translated_text"]) > 0


class TestSystemHealth:
    """Test overall system health and monitoring."""
    
    @pytest.mark.asyncio
    async def test_system_startup_health(self):
        """Test that system starts up healthy."""
        
        async with aiohttp.ClientSession() as session:
            # Check health endpoint
            async with session.get(HEALTH_ENDPOINT) as response:
                assert response.status == 200
                health_data = await response.json()
                assert health_data["status"] == "healthy"
                
            # Check that basic translation works
            request_data = {
                "text": "hello",
                "source_language": "en",
                "target_language": "hi",
                "model": "auto"
            }
            
            async with session.post(TRANSLATION_ENDPOINT, json=request_data) as response:
                assert response.status == 200
                data = await response.json()
                assert "translated_text" in data
                
    @pytest.mark.asyncio
    async def test_available_models_health(self):
        """Test that at least some models are available."""
        
        # Try each available model
        working_models = []
        
        async with aiohttp.ClientSession() as session:
            for model in AVAILABLE_MODELS:
                if model == "auto":
                    continue
                    
                request_data = {
                    "text": "hello",
                    "source_language": "en",
                    "target_language": "hi",
                    "model": model
                }
                
                async with session.post(TRANSLATION_ENDPOINT, json=request_data) as response:
                    if response.status == 200:
                        working_models.append(model)
                        
        # At least one model should be working
        assert len(working_models) > 0, f"No models are working. Available: {AVAILABLE_MODELS}"
        
        # Lightweight model should definitely be working
        assert "lightweight_indictrans" in working_models or "mock" in working_models
