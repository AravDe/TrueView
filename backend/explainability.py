import os
# import google.generativeai as genai
from openai import AsyncOpenAI

from typing import Dict, Any

class ExplainabilityEngine:
    
    def __init__(self, local_model: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b"), local_url: str = "http://localhost:11434/v1"):
        """
        Initialize the ExplainabilityEngine to use a local LLM.
        
        Args:
            local_model (str): Name of the local model to use (e.g., 'llama3.1:8b').
            local_url (str): URL of the local inference server.
        """
        # self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        # if self.api_key:
        #     genai.configure(api_key=self.api_key)
        #     self.model = genai.GenerativeModel('gemini-flash-latest')

        self.local_model = local_model

        self.client = AsyncOpenAI(
            base_url=local_url,
            api_key="not-needed" # Local servers usually don't enforce API keys
        )

    async def _generate_content(self, prompt: str) -> str:
        """Helper to generate content from the configured local LLM."""
        response = await self.client.chat.completions.create(
            model=self.local_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
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
        verdict = API_results['ai_detected']
        confidence = API_results['ai_confidence']
        
        
        if media_type == 'video':
            prompt = await self._build_video_overall_prompt(metadata, metrics, verdict= verdict, confidence= confidence)
        else:
            prompt = await self._build_image_overall_prompt(metadata, metrics, verdict=verdict, confidence=confidence)
        
        try:
            # response = self.model.generate_content(prompt)
            # return response.text
            return await self._generate_content(prompt)
        except Exception as e:
            return f"Error generating explanation: {str(e)}"
    
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
        


    
    async def _build_video_overall_prompt(self, metadata: Dict[str, Any], metrics: Dict[str, Any], verdict, confidence) -> str:
        prompt = f"""You are an AI deepfake detection expert explaining analysis results to a non-technical user. You are not to form your own conclusions, but use the
        metrics provided to support the expert opinion given by the verdict and the confidence level. You are to explain why some metric is high or low with reference to 
        these verdicts and confidence.

**Context:** A video file has been analyzed for signs of AI generation or manipulation.

**Video Information:**
- Duration: {metadata['duration']:.2f} seconds
- Frame Count: {metadata['frame_count']} frames
- Resolution: {metadata['width']}x{metadata['height']}
- FPS: {metadata['fps']:.2f}

**Analysis Metrics:**
- Average Motion: {metrics['avg_motion']:.2f}
- Motion Standard Deviation: {metrics['motion_std']:.2f}
- Average Edge Consistency: {metrics['avg_edge_consistency']:.2f} (std: {metrics['edge_std']:.2f})
- Average Texture Variance: {metrics['avg_texture_variance']:.2f} (std: {metrics['texture_std']:.2f})

**Verdict and Confidence**
- Verdict: {verdict}
- Confidence: {confidence:.2f}

| **Metric**                    | **Description**                                                                                                       |                             **Reference Range (Authentic Video)**                            |                                             **Suspicious Range (Possible AI / Interpolated)**                                             
| :---------------------------- | :-------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------: | :---------------------------------------------------------------------------------------------------------------------------------------: 
| **Average Motion**            | Measures overall pixel intensity change between consecutive frames. Reflects how much movement occurs frame to frame. |       **10 – 50** → Real footage has natural hand motion, jitter, or parallax changes.       | **< 10** → Overly smooth, AI-interpolated or generated video. **> 50** → Possible frame drops, stuttering, or synthetic motion artifacts.
| **Motion Standard Deviation** | Captures how *varied* the motion is across the video sequence.                                                        |           **5 – 20** → Indicates realistic variation from slow and fast movements.           |           **< 5** → Motion too uniform (AI smoothing). **> 20** → Erratic frame differences (glitchy or synthetic transitions).          
| **Edge Consistency**          | Measures how stable detected edges remain between frames — real edges change due to lighting, focus, and parallax.    |       **5 – 30** → Real videos show edge fluctuation as lighting and perspective shift.      |              **< 5** → Edges too stable (AI). **> 30** → Edge distortion or flickering (over-generated or poorly composited).            
| **Texture Variance**          | Measures overall frame-to-frame variation in fine detail (e.g., fur, grass, reflections).                             | **100 – 10,000** → Real videos have high diversity depending on surface detail and lighting. |       **< 100** → Overly clean, uniform surfaces (AI diffusion). **> 10,000** → Possibly noise injection or low-quality compression.     


**Task:** Provide a concise, easy-to-understand explanation of whether this video appears authentic or AI-generated. 
Focus on:
1. Overall conclusion (likely authentic or AI-generated)
2. Main reasoning behind the conclusion
3. Which patterns are most significant
4. Confidence level in the assessment

Make it into a short paragraph mentioning only the most significant signs according to the metrics with ABSOLUTELY NO FORMATTING ANYWHERE. The paragraph should be about 5-6 lines at best"""

        return prompt
    




    
    async def _build_image_overall_prompt(self, metadata: Dict[str, Any], metrics: Dict[str, Any], verdict, confidence) -> str:
        """Build prompt for overall image analysis explanation."""
        prompt = f"""You are an AI deepfake detection expert explaining analysis results to a non-technical user. You are not to form your own conclusions, but use the
        metrics provided to support the expert opinion given by the verdict and the confidence level. You are to explain why some metric is high or low with reference to 
        these verdicts and confidence.

**Context:** An image file has been analyzed for signs of AI generation.

**Image Information:**
- Resolution: {metadata['width']}x{metadata['height']}

**Analysis Metrics:**
- Texture Variance: {metrics['avg_texture_variance']:.2f} (std: {metrics['texture_std']:.2f})
- Edge Density: {metrics['edge_density']:.4f}
- Color Variance: {metrics['color_variance']:.2f}
- Edge Continuity: {metrics['edge_continuity']:.2f}

**Verdict and Confidence**
- Verdict: {verdict}
- Confidence: {confidence:.2f}

| **Metric**           | **Description**                                                                               | **Typical Range (Authentic Frame)** |                    **Suspicious Range (AI/Generated)**                    
| :------------------- | :-------------------------------------------------------------------------------------------- | :---------------------------------: | :----------------------------------------------------------------------: 
| **Texture Variance** | Measures local variance of fine details (fur, grass, skin).                                   |             **250–600**             |                  **< 200** → Overly smooth, fake texture                 
| **Edge Density**     | Ratio of detected edges to total pixels — shows how detailed or sharp an image is.            |            **0.03–0.10**            | **< 0.02** → Blurry, **> 0.12** → Oversharpened or artificially enhanced 
| **Color Variance**   | Measures diversity in color saturation and hue distribution.                                  |            **3000–8000**            |     **< 2500** → Overly uniform palette, **> 10000** → Over-saturated    
| **Edge Continuity**  | Average contour length across all detected edges — shows how continuous vs. broken edges are. |   **20–80 px avg contour length**   |  **< 15** → Fragmented edges, **> 90** → Melting or overconnected edges  |


**Task:** Provide a comprehensive, easy-to-understand explanation of whether this image appears authentic or AI-generated.
Focus on:
1. Overall conclusion (likely authentic or AI-generated)
2. Main reasoning behind the conclusion
3. Which visual characteristics are most telling
4. Confidence level in the assessment
Do not mention raw metrics just describe the high metrics as features that can be seen on an image with those metric scores
Make it into a short paragraph mentioning only the most significant signs according to the metrics with ABSOLUTELY NO FORMATTING ANYWHERE. The paragraph should be about 5-6 lines at best"""

        return prompt
    




    
    async def _build_video_metrics_prompt(self, metrics: Dict[str, Any]) -> str:
        """Build prompt for metric-focused video explanation."""
        prompt = f"""You are an AI deepfake detection expert. Provide a SHORT, metric-focused analysis.

**Video Metrics:**
- Average Motion: {metrics['avg_motion']:.2f}
- Motion Standard Deviation: {metrics['motion_std']:.2f}
- Average Edge Consistency: {metrics['avg_edge_consistency']:.2f} (std: {metrics['edge_std']:.2f})
- Average Texture Variance: {metrics['avg_texture_variance']:.2f} (std: {metrics['texture_std']:.2f})

**Normal Ranges:**
- Motion: 10-50
- Motion std: 5-20
- Edge Consistency: 5-30, Edge std: 2-15
- Texture Variance: 100-10000, Texture std: 50-5000

**Task:** In 3-5 bullet points, explain what each metric value indicates:
- State if each metric is within normal range, suspiciously low, or suspiciously high
- Explain what the deviation means to someone non technical, make sure you use real world examples to explain terms. (e.g., "unusually low motion suggests synthetic frames")
- Highlight the most suspicious metric(s)

Be concise and technical. Focus on the numbers.ABSOLUTELY NO FORMATTING ANYWHERE"""

        return prompt
    





    async def _build_image_metrics_prompt(self, metrics: Dict[str, Any]) -> str:
        """Build prompt for metric-focused image explanation."""
        prompt = f"""You are an AI deepfake detection expert. Provide a SHORT, metric-focused analysis.

**Image Metrics:**
- Texture Variance: {metrics['avg_texture_variance']:.2f} (std: {metrics['texture_std']:.2f})
- Edge Density: {metrics['edge_density']:.4f}
- Color Variance: {metrics['color_variance']:.2f}
- Edge Continuity: {metrics['edge_continuity']:.2f}

**Normal Ranges:**
- Texture Variance: 100-10000
- Edge Density: 0.05-0.20
- Color Variance: 500-5000
- Edge Continuity: 50-500

**Task:** In 3-5 bullet points, explain what each metric value indicates:
- State if each metric is within normal range, suspiciously low, or suspiciously high
- Explain what the deviation means, to someone non technical, make sure you use real world examples to explain terms. (e.g., "low texture variance suggests over-smoothing typical of AI")
- Highlight the most suspicious metric(s)

Be concise and technical. Focus on the numbers. ABSOLUTELY NO FORMATTING ANYWHERE"""

        return prompt
    
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
        
        prompt = f"""You are an AI deepfake detection expert. Analyze this single metric from a video.

**Metric:** {config['display_name']}
**Description:** {config['description']}
**Actual Value:** {actual_value:.2f}
**Expected Range:** {config['expected_range']}
**Status:** {'Within normal range' if status == 'normal' else 'Outside normal range'}

**Task:** Provide a 2-3 sentence analysis explaining:
1. What this specific value indicates about the video
2. Whether it suggests authenticity or AI generation
3. Use real-world examples to explain (e.g., "like a camera held perfectly still" or "like natural hand shake")

Be concise, conversational and accessible to non-technical users. ABSOLUTELY NO FORMATTING ANYWHERE"""

        try:
            # response = self.model.generate_content(prompt)
            # analysis = response.text
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
        
        prompt = f"""You are an AI deepfake detection expert. Analyze this single metric from an image.

**Metric:** {config['display_name']}
**Description:** {config['description']}
**Actual Value:** {actual_value:.4f}
**Expected Range:** {config['expected_range']}
**Status:** {'Within normal range' if status == 'normal' else 'Outside normal range'}

**Task:** Provide a 2-3 sentence analysis explaining:
1. What this specific value indicates about the image
2. Whether it suggests authenticity or AI generation
3. Use real-world examples to explain (e.g., "like an overly smooth skin texture" or "like natural photo grain")

Be concise, conversational and accessible to non-technical users. ABSOLUTELY NO FORMATTING ANYWHERE."""

        try:
            # response = self.model.generate_content(prompt)
            # analysis = response.text
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