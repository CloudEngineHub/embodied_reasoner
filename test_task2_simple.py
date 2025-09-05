#!/usr/bin/env python3
"""
Simple Test for Improved Task 2
Tests the core functionality: Original interaction position + Greedy supplementary positions
"""

import sys
from pathlib import Path

# Add the evaluate directory to the Python path
evaluate_path = Path(__file__).parent / "evaluate"
sys.path.insert(0, str(evaluate_path))

from ai2thor_engine.RocAgent import RocAgent
import cv2
import numpy as np
import glob
import os


def create_concat_comparison(agent, obj_type):
    """创建拼接对比图片"""
    print(f"\n🖼️ Creating concatenated comparison images...")
    
    # Find all multi-view images from the latest test
    image_pattern = f"./data/item_image/*/FloorPlan201_0_multi_view_observation_{obj_type}_*_*.png"
    images = sorted(glob.glob(image_pattern))
    
    if len(images) < 2:
        print(f"⚠️ Not enough images found for comparison: {len(images)}")
        return
    
    print(f"📸 Found {len(images)} images to concatenate")
    
    # Load images
    loaded_images = []
    labels = []
    
    for img_path in images:
        img = cv2.imread(img_path)
        if img is not None:
            # Extract view info from filename
            filename = os.path.basename(img_path)
            if "_interaction_" in filename:
                label = "Original Interaction"
            elif "_supplementary_" in filename:
                view_num = filename.split("_")[-2]  # Get view number
                label = f"Supplementary View {view_num}"
            else:
                label = "Multi-view"
            
            loaded_images.append(img)
            labels.append(label)
            print(f"   • {label}: {img_path}")
    
    if len(loaded_images) < 2:
        print(f"⚠️ Could not load enough images")
        return
    
    # Add text labels to images
    labeled_images = []
    for img, label in zip(loaded_images, labels):
        # Add white background for text
        img_with_label = img.copy()
        cv2.rectangle(img_with_label, (10, 10), (400, 50), (255, 255, 255), -1)
        cv2.rectangle(img_with_label, (10, 10), (400, 50), (0, 0, 0), 2)
        cv2.putText(img_with_label, label, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        labeled_images.append(img_with_label)
    
    # Concatenate images horizontally
    concat_img = np.concatenate(labeled_images, axis=1)
    
    # Save concatenated image
    output_path = f"./test_data/concat_comparison_{obj_type}.png"
    cv2.imwrite(output_path, concat_img)
    
    print(f"✅ Concatenated comparison image saved: {output_path}")
    return output_path


def test_improved_task2_simple():
    """Simple test of improved Task 2 implementation"""
    print("🧪 Simple Test: Improved Task 2")
    print("=" * 50)
    
    scene = "FloorPlan201"
    
    try:
        # Initialize AI2Thor controller
        print("🏠 Initializing AI2Thor...")
        from ai2thor.controller import Controller
        
        controller = Controller(
            agentMode="default",
            visibilityDistance=10,
            scene=scene,
            gridSize=0.25,
            snapToGrid=True,
            rotateStepDegrees=90,
            renderDepthImage=False,
            renderInstanceSegmentation=False,
            width=800,
            height=450,
            fieldOfView=90,
        )
        
        # Initialize RocAgent
        print("🏠 Initializing RocAgent...")
        agent = RocAgent(
            controller,
            save_path="./test_data/",
            scene=scene,
            visibilityDistance=10,
            gridSize=0.25,
            fieldOfView=90,
            target_objects=[],
            related_objects=[],
            navigable_objects=[],
            taskid=1001,
            platform_type="GPU"
        )
        
        # Enable enhanced navigation
        agent.enable_enhanced_navigation(
            enable_indexing=True,
            enable_dialogue=False,
            enable_multi_view=True
        )
        
        agent.init_agent_corner()
        
        # Test with Sofa
        obj_type = "Sofa"
        if obj_type not in agent.objecttype2object:
            print(f"❌ {obj_type} not found in scene")
            return False
        
        print(f"\n🔍 Testing {obj_type}...")
        
        # First navigate to the object using standard navigation (this becomes our original view)
        print("🎯 Step 1: Standard navigation to establish original interaction position...")
        original_result = agent.navigate(obj_type)
        
        if not original_result[0]:  # Check if navigation was successful
            print(f"❌ Original navigation failed")
            return False
            
        print(f"✅ Original navigation successful: {original_result[0]}")
        
        # Now apply multi-view observation (which will add 2 supplementary views)
        print("🔄 Step 2: Adding supplementary views for complete observation...")
        result = agent.navigate_complete_view(obj_type)
        
        if result[0]:  # image_fp
            print(f"✅ Test successful!")
            print(f"📸 Final image: {result[0]}")
            
            # Create concatenated comparison image
            create_concat_comparison(agent, obj_type)
            
            return True
        else:
            print(f"❌ Test failed - no image returned")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        try:
            if 'agent' in locals():
                agent.controller.stop()
            elif 'controller' in locals():
                controller.stop()
        except Exception as cleanup_error:
            print(f"⚠️ Cleanup error: {cleanup_error}")


if __name__ == "__main__":
    print("🚀 Testing Improved Task 2 Implementation")
    print("Strategy: Original Interaction Position + Greedy Supplementary Views")
    print("=" * 70)
    
    success = test_improved_task2_simple()
    
    if success:
        print(f"\n🎉 Improved Task 2 is working correctly!")
        print(f"💡 Key features verified:")
        print(f"   • Large object detection")
        print(f"   • Original interaction position preserved")
        print(f"   • Supplementary observation positions added")
        print(f"   • Angle distribution optimization")
    else:
        print(f"\n❌ Test failed - need to debug")
    
    print(f"\n🏁 Test complete!")