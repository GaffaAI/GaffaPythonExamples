## Automated Form Filling with Parse JSON

Code example showing how to use the **Gaffa Browser Request API** to:

- **Extract** all fields from a web form using the `parse_json` action (structured schema output)
- **Prompt** you in the terminal for values
- **Fill & submit** the form in a real browser session using `type` + `click`
- **Capture a screenshot** after submission

This is designed automation workflows where you want **schema‑driven extraction** plus a simple **human‑in‑the‑loop** data entry step.

## Files

| File | Description |
|---|---|
| `automated_form_filling.py` | Extracts form fields with `parse_json`, prompts for input, fills and submits the form, captures a screenshot |

## Requirements

- Python 3.8+
- A Gaffa API key — sign up at [gaffa.dev](https://gaffa.dev) and create your key in the **API Keys** section of the dashboard

## Setup

**1. Install dependencies**

```bash
pip install requests
```

**2. Add your API key**

In `automated_form_filling.py`, set:

- `GAFFA_API_KEY = "your_api_key_here"`

(Alternatively, you can export it as an environment variable and load it in code.)

**3. (Optional) Choose a form URL**

Update `FORM_URL` in `automated_form_filling.py` to the form you want to analyze and fill.

## How it works

### Step 1 — Extract fields (Parse JSON)

The script opens the form URL and runs actions:

- `wait` for `form` to appear
- `parse_json` with a schema:
  - `form_title`
  - `fields[]` with: `label`, `field_name`, `field_type`, `required`, `placeholder`

It then reads the `parse_json` action’s `output` from the response.

### Step 2 — Collect values (Terminal prompt)

For each extracted field, the script prompts you for a value:

- Required fields keep prompting until you enter something
- Optional fields can be skipped by pressing Enter

### Step 3 — Fill, submit & screenshot

The script builds a second action list:

- `wait` for `form`
- `type` into each input using the selector: `[name='<field_name>']`
- `click` the submit button: `button[type='submit']`
- `capture_screenshot` (fullscreen)

If present, the screenshot is printed from the `capture_screenshot` action `output`.

## Usage

From this folder:

```bash
python automated_form_filling.py
```

You’ll see:

- “Step 1: Analyzing form…”
- A guided prompt to enter values
- A summary of what will be submitted
- A confirmation prompt (`Submit this form? (y/n)`)
- Submission result + screenshot output (if returned)

## Notes

- **Selectors assume `name` attributes**: Filling uses `[name='...']`. If your target form doesn’t use `name`, update the extraction schema to capture a usable selector (e.g., `id`, `aria-label`, or a stable CSS selector).
- **Modals / load delays**: If the page loads slowly or shows a modal, adjust the `wait` action timeout or add additional waits/clicks as needed.
- **Model choice**: `parse_json` is configured with `model: "gpt-4o-mini"`. You can switch models depending on your accuracy/cost needs.