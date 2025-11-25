"""
Quick test to verify all models can be imported and have proper config.
Run this BEFORE deploying to HF Spaces to catch any issues.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_model_imports():
    """Test that all models can be imported without errors."""
    print("Testing model imports...")
    
    try:
        from models import (
            CurriculumMarkdown,
            InstructionMarkdown,
            PracticeMarkdown,
            QualityAssessment,
            CourseCompletion,
            LearningObjective,
            Lesson,
            Module,
            Curriculum,
            InstructionSection,
            Instruction,
            PracticeExercise,
            Assessment,
            Practice,
            QualityIssue,
            QualityAssurance
        )
        print("✅ All models imported successfully")
        
        # Test model config
        models_to_check = [
            CurriculumMarkdown,
            InstructionMarkdown,
            PracticeMarkdown,
            QualityAssessment,
            CourseCompletion,
            LearningObjective,
            Lesson,
            Module,
            Curriculum,
            InstructionSection,
            Instruction,
            PracticeExercise,
            Assessment,
            Practice,
            QualityIssue,
            QualityAssurance
        ]
        
        print("\nChecking model configs...")
        for model in models_to_check:
            config = model.model_config
            if config.get("extra") != "forbid":
                print(f"❌ {model.__name__}: extra should be 'forbid', got {config.get('extra')}")
                return False
            else:
                print(f"✅ {model.__name__}: config OK")
        
        print("\n✅ All models have correct configuration!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_json_schema():
    """Test that models can generate JSON schema without errors."""
    print("\nTesting JSON schema generation...")
    
    try:
        from models import CourseCompletion, QualityAssessment
        
        # Try to get the schema (this is what Gradio does)
        schema = CourseCompletion.model_json_schema()
        print(f"✅ CourseCompletion schema generated: {len(str(schema))} chars")
        
        schema2 = QualityAssessment.model_json_schema()
        print(f"✅ QualityAssessment schema generated: {len(str(schema2))} chars")
        
        # Check for problematic additionalProperties
        import json
        schema_str = json.dumps(schema)
        if '"additionalProperties": true' in schema_str:
            print("❌ Found 'additionalProperties: true' in schema!")
            return False
        else:
            print("✅ No problematic additionalProperties found")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*70)
    print("PYDANTIC MODEL VALIDATION TEST")
    print("="*70)
    print()
    
    test1 = test_model_imports()
    test2 = test_json_schema()
    
    print()
    print("="*70)
    if test1 and test2:
        print("✅ ALL TESTS PASSED - Safe to deploy!")
    else:
        print("❌ TESTS FAILED - Fix issues before deploying!")
    print("="*70)
    
    sys.exit(0 if (test1 and test2) else 1)
