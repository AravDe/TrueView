import sys
from pathlib import Path
import time

# Add project root to sys.path to allow imports from backend
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent.parent
sys.path.append(str(project_root))

from backend.attrClassifier import MediaAnalyzer
from backend.explainability import ExplainabilityEngine

start_time = time.time()    

video_path = str(project_root / 'media' / 'lion_ai_video.mp4')
image_path = str(project_root / 'media' / 'ai_cow.png')

analyzer = MediaAnalyzer()
video_results = analyzer.analyze_video(video_path)
image_results = analyzer.analyze_image(image_path)

# Mock API results for demonstration
video_api_results = {'ai_detected': 'fake', 'ai_confidence': 0.95}

explainer = ExplainabilityEngine()

# print("=" * 80)
# print("VIDEO ANALYSIS - OVERALL EXPLANATION")
# print("=" * 80)
# overall_video = explainer.explain_overall_analysis(video_results, video_api_results)
# print(overall_video)
# print("\n")

print("=" * 80)
print("VIDEO ANALYSIS - METRIC-FOCUSED EXPLANATION")
print("=" * 80)
metrics_video = explainer.explain_specific_metrics(video_results)
print(metrics_video)
print("\n")

print("=" * 80)
print("INDIVIDUAL METRIC ANALYSIS - VIDEO")
print("=" * 80)

video_metrics_to_analyze = ['avg_motion', 'motion_std', 'avg_edge_consistency', 'avg_texture_variance']
for metric in video_metrics_to_analyze:
    result = explainer.explain_individual_metric(video_results, metric)
    print(f"\n📊 {result['display_name']}")
    print(f"   Actual Value: {result['actual_value']:.2f}")
    print(f"   Expected Range: {result['expected_range']}")
    print(f"   Status: {result['status'].upper()}")
    print(f"   Analysis: {result['analysis']}")

end_time = time.time()
elapsed_time = end_time - start_time
print(f"\nTest completed in {elapsed_time:.2f} seconds.")