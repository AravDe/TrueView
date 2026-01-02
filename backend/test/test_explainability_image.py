import sys
from pathlib import Path
import time, asyncio

script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent.parent
sys.path.append(str(project_root))

from backend.attrClassifier import MediaAnalyzer
from backend.explainability import ExplainabilityEngine

async def test_image():
    start_time = time.time()    
    image_path = str(project_root / 'media' / 'ai_cow.png')

    analyzer = MediaAnalyzer()
    image_results = analyzer.analyze_image(image_path)

    image_api_results = {'ai_detected': 'real', 'ai_confidence': 0.10}

    explainer = ExplainabilityEngine()

    print("\n")
    print("=" * 40)
    print("INDIVIDUAL METRIC ANALYSIS - IMAGE")
    print("=" * 40)

    metrics = ['avg_texture_variance', 'edge_density', 'color_variance', 'edge_continuity']
    tasks = [explainer.explain_individual_metric(image_results, metric_name) for metric_name in metrics]
    results = await asyncio.gather(*tasks)

    for result in results:
        print(f"\n📊 {result['display_name']}")
        print(f"   Actual Value: {result['actual_value']:.4f}")
        print(f"   Expected Range: {result['expected_range']}")
        print(f"   Status: {result['status'].upper()}")
        print(f"   Analysis: {result['analysis']}")

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\nTest completed in {elapsed_time:.2f} seconds.")

asyncio.run(test_image())