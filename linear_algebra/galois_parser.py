"""
Galois Field Question Parser & Parameter Extraction Engine
Parses natural language questions, mathematical text, or OCR inputs
to extract field notation, modulus, elements, operations, and required tasks.
"""

import re

def extract_field_parameters(question_text):
    """
    Extracts structured mathematical parameters from a question string.
    Returns dict containing field_notation, modulus, elements, operations, task, and confidence.
    """
    if not question_text or not isinstance(question_text, str):
        text = ""
    else:
        text = question_text.strip()

    # Default parameters
    modulus = 2
    elements = [0, 1]
    field_notation = "F₂"
    task = "verify_field_axioms"
    task_display = "Verify Field Axioms"
    is_prime = True

    if not text:
        return {
            'question_raw': "",
            'field_notation': "F₂",
            'modulus': 2,
            'is_prime': True,
            'elements': [0, 1],
            'operations': {
                'addition': 'modular',
                'multiplication': 'modular'
            },
            'task': 'verify_field_axioms',
            'task_display': 'Verify Field Axioms',
            'confidence': 1.0,
            'extracted_automatically': False,
            'warnings': []
        }

    warnings = []

    # 1. Detect Modulus & Field Notation
    # Match patterns like F_2, F2, F₂, GF(2), Z_2, Z2, Z₂, mod 2, modulo 2, F_3, F3, F₃, etc.
    mod_patterns = [
        (r'(?:GF|F|Z|f|z)[_\s]*\(?\s*(\d+)\s*\)?', 1),
        (r'[Ff][\textsubscript0-9]*([0-9]+)', 1),
        (r'(?:mod|modulo)\s*(\d+)', 1),
        (r'\{0\s*,\s*1\s*,\s*2\s*,\s*3\s*,\s*4\s*,\s*5\s*,\s*6\}', 7),
        (r'\{0\s*,\s*1\s*,\s*2\s*,\s*3\s*,\s*4\}', 5),
        (r'\{0\s*,\s*1\s*,\s*2\s*,\s*3\}', 4),
        (r'\{0\s*,\s*1\s*,\s*2\}', 3),
        (r'\{0\s*,\s*1\}', 2)
    ]

    detected_mod = None
    for pattern, grp in mod_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                if isinstance(grp, int):
                    val = int(match.group(grp))
                else:
                    val = grp
                if 2 <= val <= 29:
                    detected_mod = val
                    break
            except Exception:
                pass

    if detected_mod:
        modulus = detected_mod
    else:
        # Check explicit set representation in text
        set_match = re.search(r'\{([0-9,\s]+)\}', text)
        if set_match:
            try:
                nums = [int(n.strip()) for n in set_match.group(1).split(',') if n.strip().isdigit()]
                if nums and nums[0] == 0:
                    modulus = len(nums)
            except Exception:
                pass

    # Check primality helper
    def check_is_prime(n):
        if n < 2: return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0: return False
        return True

    is_prime = check_is_prime(modulus)
    elements = list(range(modulus))
    
    # Subscript formatting for display
    subscript_map = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    field_notation = f"F{str(modulus).translate(subscript_map)}"

    # 2. Detect Task
    text_lower = text.lower()
    if any(k in text_lower for k in ["inverse", "inverses", "additive inverse", "multiplicative inverse"]):
        if any(k in text_lower for k in ["axiom", "verify field", "all axioms"]):
            task = "verify_field_axioms"
            task_display = f"Verify All Field Axioms & Inverses for {field_notation}"
        else:
            task = "find_inverses"
            task_display = f"Determine Additive & Multiplicative Inverses in {field_notation}"
    elif any(k in text_lower for k in ["table", "tables", "addition table", "multiplication table", "cayley"]):
        if "verify" in text_lower:
            task = "verify_field_axioms"
            task_display = f"Construct Tables & Verify Field Axioms for {field_notation}"
        else:
            task = "construct_tables"
            task_display = f"Construct Addition & Multiplication Tables for {field_notation}"
    elif any(k in text_lower for k in ["is a field", "determine whether", "check field", "is it a field"]):
        task = "check_field"
        task_display = f"Determine whether {field_notation} is a Field"
    else:
        task = "verify_field_axioms"
        task_display = f"Verify Field Axioms for {field_notation}"

    if not is_prime:
        warnings.append(f"{field_notation} (modulus {modulus}) is not prime. Simple integer modular arithmetic Z_{modulus} contains zero-divisors and is a Ring, not a Field.")

    return {
        'question_raw': text,
        'field_notation': field_notation,
        'modulus': modulus,
        'is_prime': is_prime,
        'elements': elements,
        'operations': {
            'addition': f'modulo {modulus}',
            'multiplication': f'modulo {modulus}'
        },
        'task': task,
        'task_display': task_display,
        'confidence': 0.95 if detected_mod else 0.75,
        'extracted_automatically': True,
        'warnings': warnings
    }
