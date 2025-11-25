from models import CourseCompletion
import json

schema = CourseCompletion.model_json_schema()
schema_str = json.dumps(schema, indent=2)

# Check for boolean additionalProperties
has_bool_additional = ('"additionalProperties": false' in schema_str or 
                       '"additionalProperties": true' in schema_str)

print(f"Has boolean additionalProperties: {has_bool_additional}")

if has_bool_additional:
    print("\n❌ PROBLEM: Found boolean additionalProperties in schema")
    # Show where it appears
    lines = schema_str.split('\n')
    for i, line in enumerate(lines):
        if 'additionalProperties' in line and ('false' in line or 'true' in line):
            print(f"Line {i}: {line}")
else:
    print("\n✅ GOOD: No boolean additionalProperties found")

print(f"\nSchema size: {len(schema_str)} characters")
print(f"Top-level keys: {list(schema.keys())}")
