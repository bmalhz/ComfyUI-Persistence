# PersistImageBank

This node adds persistence for the `image` type.

## Parameters

- **cache_name**: Name of the configured cache (currently only `default` is supported).  
- **bank_name**: Name of the bank (used as a top-level storage prefix).  
- **bank_id**: ID of this bank (used as a subprefix). If **string**, used as-is; otherwise the node uses `sha256(str(bank_id))`. Avoid unsafe characters in string IDs; keys are normalized/percent-encoded for filesystem safety.  
- **selected_index**: Python-style index of the image to output on `selected_index` (negative indices supported). **Default:** `0`. Out-of-range index raises an error.  
- **enable_write**: Whether to save the Image(s) to storage when creating a new bank. **Default:** `true`.  
- **[images]**: Optional input images.

## Usage

- **If `images` are provided**
  - **Bank exists** → input images are ignored; stored images are loaded and sent to outputs.  
  - **Bank does not exist** → if **enable_write** is `true`, input images are saved and passed through; if `false`, input images are passed through but not saved.

- **If `images` are not provided**
  - **Bank exists** → stored images are loaded and sent to outputs.  
  - **Bank does not exist** → an exception is raised.

## Outputs

- **images**: full batch of images.  
- **selected_index**: single image at the configured index.
