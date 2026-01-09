# ComfyUI-Persistence

This project provides a ComfyUI custom node to persist intermediate images to avoid recomputation accross workflows runs.

It makes it possible to:
- Restart ComfyUI and resume your workflow with previously computed `image` steps
- Reuse persisted `images` across different workflows

*Note: this project is still a work in progress!*

![Diagram](doc/architecture.drawio.svg)

## Features
- `PersistImageBank` node for persisting images.
- `PersistSteppedImageBank` for chaining sequences of images.
- Persists images in `WebP` format (size-optimized and viewable in common image viewers) or `safetensors.zst`.

## Installation
Clone this project to your `<ComfyUI-path>/custom_nodes/` folder.
```bash
cd custom_nodes
git clone https://github.com/bmalhz/ComfyUI-Persistence.git
```

Note: availability through the `Registry` will come soon.

## Configuration
You need to create the `persistence.json` file into your ComfyUI `user` directory (`comfyui/user` by default unless you have set a custom location using `--user-directory`):
```json
{
  "default": {
    "cache_path": "<absolute-path-to-the-save-location>",
    "encoder": "pil"
  }
}
```

## Usage

### Inputs

**bank_id** — allowed types and behavior:
- **string**: used verbatim as the subfolder name inside the `bank_name` folder.
- **any JSON-encodable value**: the value is JSON-encoded and a SHA-256 fingerprint of that encoding is used as the subfolder name. Any change to the encoded value produces a different fingerprint and therefore a different subfolder.

**selected_index** — selects which single image is emitted to the `selected_image` output. Indexing is zero-based.

**bank_name** — used verbatim as the root folder name for this bank.

#### Notes and edge cases
- **JSON encoding**: the fingerprint depends on the exact JSON encoding. Different encoders or formatting (for example, key order in objects) may produce different fingerprints for semantically identical values. Use a canonical JSON encoder if stable folder names are required.
- **Collisions**: SHA-256 collisions are extremely unlikely; no special collision handling is implemented.
- **String restrictions**: if `bank_id` is a string, ensure it contains only filesystem-safe characters; otherwise the folder creation may fail or be sanitized.

#### Example
- `bank_name`: `my_bank`  
- `bank_id` as string: `"customer-123"` → folder: `my_bank/customer-123`  
- `bank_id` as JSON object: `{"user": "alice", "tier": 2}` → JSON-encode → SHA-256 → folder: `my_bank/<sha256-fingerprint>`  
- `selected_index`: `0` → the first image is sent to `selected_image`.
