from typing import Dict, Any

async def build_video_overall_prompt(metadata: Dict[str, Any], metrics: Dict[str, Any], verdict, confidence) -> str:
    prompt = f"""Role: Deepfake detection expert.
Task: Explain the analysis verdict to a user in 3-4 sentences.
Context: Video ({metadata['duration']:.1f}s, {metadata['width']}x{metadata['height']}).
Verdict: {verdict} (Confidence: {confidence*100:.1f}%).

Metrics (Value vs Normal Range):
- Motion: {metrics['avg_motion']:.1f} (10-50)
- Motion Std: {metrics['motion_std']:.1f} (5-20)
- Edge Consistency: {metrics['avg_edge_consistency']:.1f} (5-30)
- Texture Variance: {metrics['avg_texture_variance']:.1f} (100-10k)

Explain why the video is likely {verdict} based on the most significant metrics. Be concise. No formatting."""
    return prompt

async def build_image_overall_prompt(metadata: Dict[str, Any], metrics: Dict[str, Any], verdict, confidence) -> str:
    """Build prompt for overall image analysis explanation."""
    prompt = f"""Role: Deepfake detection expert.
Task: Explain the analysis verdict to a user in 3-4 sentences.
Context: Image ({metadata['width']}x{metadata['height']}).
Verdict: {verdict} (Confidence: {confidence*100:.1f}%).

Metrics (Value vs Normal Range):
- Texture Variance: {metrics['avg_texture_variance']:.1f} (250-600)
- Edge Density: {metrics['edge_density']:.3f} (0.03-0.10)
- Color Variance: {metrics['color_variance']:.1f} (3000-8000)
- Edge Continuity: {metrics['edge_continuity']:.1f} (20-80)

Explain why the image is likely {verdict} based on the most significant metrics. Be concise. No formatting."""
    return prompt

def build_single_metric_prompt(media_type: str, config: Dict[str, Any], actual_value: float, status: str) -> str:
    status_text = 'Within normal range' if status == 'normal' else 'Outside normal range'
    val_str = f"{actual_value:.2f}" if media_type == 'video' else f"{actual_value:.4f}"
    
    return f"""Role: Deepfake expert.
Task: Analyze this single metric in 2 sentences.
Metric: {config['display_name']} ({config['description']})
Value: {val_str} (Range: {config['expected_range']})
Status: {status_text}

Explain what this value indicates about the {media_type} (e.g., "like natural hand shake" or "artificial smoothing"). Be concise. No formatting."""
