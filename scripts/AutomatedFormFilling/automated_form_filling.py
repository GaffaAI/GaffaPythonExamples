import requests

# Configuration
GAFFA_API_KEY = (
    "sk_live_a1c8581d-39b1-433a-b0ef-928f8e577367"  # Replace with your actual API key
)
GAFFA_API_URL = "https://api.gaffa.dev/v1/browser/requests"
FORM_URL = "https://demo.gaffa.dev/simulate/form?loadTime=3&showModal=true&modalDelay=5&formType=address"


def extract_form_fields(form_url):
    """Extract all fields from a web form using Parse JSON."""
    payload = {
        "url": form_url,
        "async": False,
        "settings": {
            "record_request": False,
            "actions": [
                {"type": "wait", "selector": "form", "timeout": 10000},
                {
                    "type": "parse_json",
                    "data_schema": {
                        "name": "FormFields",
                        "description": "Extract all form input fields",
                        "fields": [
                            {
                                "type": "string",
                                "name": "form_title",
                                "description": "Form title",
                            },
                            {
                                "type": "array",
                                "name": "fields",
                                "description": "List of all input fields",
                                "fields": [
                                    {
                                        "type": "string",
                                        "name": "label",
                                        "description": "Field label",
                                    },
                                    {
                                        "type": "string",
                                        "name": "field_name",
                                        "description": "Field name attribute",
                                    },
                                    {
                                        "type": "string",
                                        "name": "field_type",
                                        "description": "Input type",
                                    },
                                    {
                                        "type": "boolean",
                                        "name": "required",
                                        "description": "Is required?",
                                    },
                                    {
                                        "type": "string",
                                        "name": "placeholder",
                                        "description": "Placeholder text",
                                    },
                                ],
                            },
                        ],
                    },
                    "instruction": "Extract all form fields with their properties",
                    "model": "gpt-4o-mini",
                    "output_type": "inline",
                },
            ],
        },
    }

    headers = {"X-API-Key": GAFFA_API_KEY, "Content-Type": "application/json"}

    try:
        response = requests.post(GAFFA_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()

        # Navigate to the correct location in response
        if "data" in result and "actions" in result["data"]:
            for action in result["data"]["actions"]:
                if action.get("type") == "parse_json" and "output" in action:
                    return action["output"]

        return None

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def collect_user_input(form_data):
    """Prompt user for values for each form field."""
    print(f"\n{'='*60}")
    print(f"📋 Form: {form_data.get('form_title', 'Unknown Form')}")
    print(f"{'='*60}\n")

    user_values = {}
    fields = form_data.get("fields", [])

    if not fields:
        print("⚠️  No fields found in the form")
        return user_values

    print(f"Please provide values for {len(fields)} field(s):\n")

    for i, field in enumerate(fields, 1):
        label = field.get("label", "Unknown Field")
        field_name = field.get("field_name", "")
        required = field.get("required", False)
        placeholder = field.get("placeholder", "")

        required_marker = " *" if required else ""
        placeholder_hint = f" (e.g., {placeholder})" if placeholder else ""
        prompt = f"[{i}/{len(fields)}] {label}{required_marker}{placeholder_hint}: "

        while True:
            value = input(prompt).strip()
            if required and not value:
                print("  ⚠️  This field is required. Please provide a value.")
                continue
            if not value and not required:
                print("  ℹ️  Skipping optional field")
                break
            user_values[field_name] = value
            break

    return user_values


def fill_form(form_url, field_values):
    """Fill out and submit the form using Gaffa."""
    if not field_values:
        return None

    # Build actions list
    actions = [{"type": "wait", "selector": "form", "timeout": 10000}]

    # Create individual type actions for each field
    for field_name, value in field_values.items():
        if value:  # Only include fields with values
            actions.append(
                {"type": "type", "selector": f"[name='{field_name}']", "text": value}
            )

    # Add click and screenshot actions
    actions.extend(
        [
            {"type": "click", "selector": "button[type='submit']"},
            {"type": "capture_screenshot", "size": "fullscreen"},
        ]
    )

    payload = {
        "url": form_url,
        "async": False,
        "settings": {"record_request": False, "actions": actions},
    }

    headers = {"X-API-Key": GAFFA_API_KEY, "Content-Type": "application/json"}

    try:
        response = requests.post(GAFFA_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Response: {e.response.text}")
        return None


def main():
    """Main function coordinating the entire process."""
    print("\n" + "=" * 60)
    print("🤖 Gaffa Form Filler")
    print("=" * 60)
    print("This tool extracts form fields and helps you fill them out.\n")

    print("📋 Step 1: Analyzing form...")
    form_data = extract_form_fields(FORM_URL)

    if not form_data:
        print("\n❌ Could not extract form fields")
        return

    print(f"✅ Found {len(form_data.get('fields', []))} field(s)\n")

    print("📝 Step 2: Collecting your input...")
    user_values = collect_user_input(form_data)

    if not user_values:
        print("\n⚠️  No values provided. Exiting.")
        return

    print(f"\n{'='*60}")
    print("📊 Summary of values to submit:")
    print(f"{'='*60}")
    for field_name, value in user_values.items():
        print(f"  {field_name}: {value}")
    print(f"{'='*60}\n")

    confirm = input("Submit this form? (y/n): ").strip().lower()
    if confirm != "y":
        print("\n❌ Submission cancelled")
        return

    print("\n🚀 Step 3: Submitting form...")
    result = fill_form(FORM_URL, user_values)

    if not result:
        print("❌ Form submission failed")
        return

    print("\n✅ Form submitted successfully!")

    # Look for screenshot in the response
    if "data" in result and "actions" in result["data"]:
        for action in result["data"]["actions"]:
            if action.get("type") == "capture_screenshot" and "output" in action:
                print(f"📸 Screenshot: {action['output']}")

    print("\n🎉 All done!\n")


if __name__ == "__main__":
    main()
