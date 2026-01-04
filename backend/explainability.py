import os, time, asyncio
from openai import AsyncOpenAI
from prompt_builder import build_video_overall_prompt, build_image_overall_prompt, build_single_metric_prompt

from typing import Dict, Any

class ExplainabilityEngine:
    
    def __init__(self, local_model: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b"), local_url: str = "http://localhost:11434/v1"):
        """
        Initialize the ExplainabilityEngine to use a local LLM.
        
        Args:
            local_model (str): Name of the local model to use (e.g., 'llama3.1:8b').
            local_url (str): URL of the local inference server.
        """

        self.local_model = local_model

        self.client = AsyncOpenAI(
            base_url=local_url,
            api_key="not-needed" # Local servers usually don't enforce API keys
        )

    async def _generate_content(self, prompt: str) -> str:
        """Helper to generate content from the configured local LLM."""
        t0 = time.time()
        response = await self.client.chat.completions.create(
            model=self.local_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        print(f"LLM Gen ({len(prompt)} chars): {time.time() - t0:.4f}s")
        return response.choices[0].message.content
    
    async def explain_overall_analysis(self, OCV_results: Dict[str, Any], API_results: Dict[str, Any])-> str:
        """
        Provides a comprehensive natural language explanation of the entire analysis,
        focusing on the overall reasoning and conclusion.
        
        Args:
            OCV_results (dict): Analysis results from MediaAnalyzer containing metadata, metrics, and raw_data
            API_results (dict): Analysis results containing 'ai_detected' and 'ai_confidence'
            
        Returns:
            str: Natural language explanation of the overall analysis
        """
        media_type = OCV_results['metadata']['type']
        metrics = OCV_results['metrics']
        metadata = OCV_results['metadata']
        
        verdict_bool = API_results.get('ai_detected') or API_results.get('deepfake_detected')
        verdict = "AI-Generated" if verdict_bool else "Authentic"
        confidence = max(API_results.get('ai_confidence', 0), API_results.get('deepfake_confidence', 0))
        
        
        if media_type == 'video':
            prompt = await build_video_overall_prompt(metadata, metrics, verdict= verdict, confidence= confidence)
        else:
            prompt = await build_image_overall_prompt(metadata, metrics, verdict=verdict, confidence=confidence)
        
        try:
            return await self._generate_content(prompt)
        except Exception as e:
            return f"Error generating explanation: {str(e)}"
    
    async def analyze_all_metrics(self, analysis_result: Dict[str, Any]) -> list:
        """
        Analyzes all metrics in the result concurrently.
        """
        metrics = analysis_result.get('metrics', {})
        tasks = [
            self.explain_individual_metric(analysis_result, metric_name) 
            for metric_name in metrics.keys()
        ]
        return await asyncio.gather(*tasks)

    async def explain_individual_metric(self, OCV_results: Dict[str, Any], metric_name: str) -> Dict[str, Any]:
        """
        Provides analysis for a single specific metric.
        
        Args:
            OCV_results (dict): Analysis results from MediaAnalyzer containing metadata, metrics, and raw_data
            metric_name (str): Name of the metric to analyze (e.g., 'avg_motion', 'edge_density')
            
        Returns:
            dict: {
                'metric_name': str,
                'display_name': str,
                'actual_value': float,
                'expected_range': str,
                'analysis': str,
                'status': str  # 'normal', 'suspicious_low', 'suspicious_high'
            }
        """
        media_type = OCV_results['metadata']['type']
        metrics = OCV_results['metrics']
        
        if media_type == 'video':
            return await self._analyze_video_metric(metrics, metric_name)
        else:
            return await self._analyze_image_metric(metrics, metric_name)
        
    async def _analyze_video_metric(self, metrics: Dict[str, Any], metric_name: str) -> Dict[str, Any]:
        """Analyze a single video metric and return structured data."""
        
        # Define metric configurations
        metric_configs = {
            'avg_motion': {
                'display_name': 'Average Motion',
                'expected_range': '10-50',
                'low_threshold': 10,
                'high_threshold': 50,
                'description': 'Measures overall pixel intensity change between consecutive frames'
            },
            'motion_std': {
                'display_name': 'Motion Standard Deviation',
                'expected_range': '5-20',
                'low_threshold': 5,
                'high_threshold': 20,
                'description': 'Captures how varied the motion is across the video sequence'
            },
            'avg_edge_consistency': {
                'display_name': 'Average Edge Consistency',
                'expected_range': '5-30',
                'low_threshold': 5,
                'high_threshold': 30,
                'description': 'Measures how stable detected edges remain between frames'
            },
            'edge_std': {
                'display_name': 'Edge Standard Deviation',
                'expected_range': '2-15',
                'low_threshold': 2,
                'high_threshold': 15,
                'description': 'Measures variation in edge consistency across frames'
            },
            'avg_texture_variance': {
                'display_name': 'Average Texture Variance',
                'expected_range': '100-10000',
                'low_threshold': 100,
                'high_threshold': 10000,
                'description': 'Measures frame-to-frame variation in fine detail'
            },
            'texture_std': {
                'display_name': 'Texture Standard Deviation',
                'expected_range': '50-5000',
                'low_threshold': 50,
                'high_threshold': 5000,
                'description': 'Measures variation in texture across frames'
            }
        }
        
        if metric_name not in metric_configs:
            return {
                'error': f"Unknown metric: {metric_name}",
                'metric_name': metric_name
            }
        
        config = metric_configs[metric_name]
        actual_value = metrics.get(metric_name, 0)
        
        # Determine status
        if actual_value < config['low_threshold']:
            status = 'suspicious_low'
        elif actual_value > config['high_threshold']:
            status = 'suspicious_high'
        else:
            status = 'normal'
        
        prompt = build_single_metric_prompt('video', config, actual_value, status)

        try:
            analysis = await self._generate_content(prompt)
        except Exception as e:
            analysis = f"Error generating analysis: {str(e)}"
        
        return {
            'metric_name': metric_name,
            'display_name': config['display_name'],
            'actual_value': actual_value,
            'expected_range': config['expected_range'],
            'description': config['description'],
            'analysis': analysis,
            'status': status
        }
    
    async def _analyze_image_metric(self, metrics: Dict[str, Any], metric_name: str) -> Dict[str, Any]:
        """Analyze a single image metric and return structured data."""
        
        # Define metric configurations
        metric_configs = {
            'avg_texture_variance': {
                'display_name': 'Texture Variance',
                'expected_range': '250-600',
                'low_threshold': 250,
                'high_threshold': 600,
                'description': 'Measures local variance of fine details (fur, grass, skin)'
            },
            'texture_std': {
                'display_name': 'Texture Standard Deviation',
                'expected_range': '100-10000',
                'low_threshold': 100,
                'high_threshold': 10000,
                'description': 'Measures variation in texture across the image'
            },
            'edge_density': {
                'display_name': 'Edge Density',
                'expected_range': '0.03-0.10',
                'low_threshold': 0.03,
                'high_threshold': 0.10,
                'description': 'Ratio of detected edges to total pixels'
            },
            'color_variance': {
                'display_name': 'Color Variance',
                'expected_range': '3000-8000',
                'low_threshold': 3000,
                'high_threshold': 8000,
                'description': 'Measures diversity in color saturation and hue distribution'
            },
            'edge_continuity': {
                'display_name': 'Edge Continuity',
                'expected_range': '20-80',
                'low_threshold': 20,
                'high_threshold': 80,
                'description': 'Average contour length across all detected edges'
            }
        }
        
        if metric_name not in metric_configs:
            return {
                'error': f"Unknown metric: {metric_name}",
                'metric_name': metric_name
            }
        
        config = metric_configs[metric_name]
        actual_value = metrics.get(metric_name, 0)
        
        # Determine status
        if actual_value < config['low_threshold']:
            status = 'suspicious_low'
        elif actual_value > config['high_threshold']:
            status = 'suspicious_high'
        else:
            status = 'normal'
        
        prompt = build_single_metric_prompt('image', config, actual_value, status)

        try:
            analysis = await self._generate_content(prompt)
        except Exception as e:
            analysis = f"Error generating analysis: {str(e)}"
        
        return {
            'metric_name': metric_name,
            'display_name': config['display_name'],
            'actual_value': actual_value,
            'expected_range': config['expected_range'],
            'description': config['description'],
            'analysis': analysis,
            'status': status
        }