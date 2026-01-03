from typing import Dict, Any

async def build_video_overall_prompt(metadata: Dict[str, Any], metrics: Dict[str, Any], verdict, confidence) -> str:
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

async def build_image_overall_prompt(metadata: Dict[str, Any], metrics: Dict[str, Any], verdict, confidence) -> str:
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

def build_single_metric_prompt(media_type: str, config: Dict[str, Any], actual_value: float, status: str) -> str:
    status_text = 'Within normal range' if status == 'normal' else 'Outside normal range'
    val_str = f"{actual_value:.2f}" if media_type == 'video' else f"{actual_value:.4f}"
    
    return f"""You are an AI deepfake detection expert. Analyze this single metric from a {media_type}.

**Metric:** {config['display_name']}
**Description:** {config['description']}
**Actual Value:** {val_str}
**Expected Range:** {config['expected_range']}
**Status:** {status_text}

**Task:** Provide a 2-3 sentence analysis explaining:
1. What this specific value indicates about the {media_type}
2. Whether it suggests authenticity or AI generation
3. Use real-world examples to explain (e.g., "like a camera held perfectly still" or "like natural hand shake")

Be concise, conversational and accessible to non-technical users. ABSOLUTELY NO FORMATTING ANYWHERE"""