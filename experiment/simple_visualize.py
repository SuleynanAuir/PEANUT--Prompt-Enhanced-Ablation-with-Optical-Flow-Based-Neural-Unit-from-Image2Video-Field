# Simple visualization using PIL
import os
import sys
import json
from PIL import Image, ImageDraw, ImageFont

def create_comparison(test_dirs, frame_num, output_path, source_frames_dir):
    """Create side-by-side comparison"""
    
    images = []
    labels = []
    
    # Load original frame
    original_patterns = [
        f'{frame_num:05d}.png',
        f'frame_{frame_num:05d}.png',
        f'frame_{frame_num:05d}.jpg'
    ]
    
    original_path = None
    for pattern in original_patterns:
        test_path = os.path.join(source_frames_dir, pattern)
        if os.path.exists(test_path):
            original_path = test_path
            break
    
    if original_path and os.path.exists(original_path):
        img = Image.open(original_path).convert('RGB')
        images.append(img)
        labels.append('Original')
    else:
        print(f'Warning: Original frame not found in {source_frames_dir}')
        print(f'  Tried: {", ".join(original_patterns)}')
        img = Image.new('RGB', (640, 480), color=(50, 50, 50))
        images.append(img)
        labels.append('Original (Missing)')
    
    # Load masks
    for test_dir in test_dirs:
        test_name = os.path.basename(test_dir)
        
        # Find mask files
        mask_files = []
        for root, dirs, files in os.walk(test_dir):
            if 'binary_masks' in root:
                # Try multiple naming patterns
                patterns = [
                    f'{frame_num:05d}.png',
                    f'frame_{frame_num:05d}_mask.png',
                    f'{frame_num:05d}_mask.png'
                ]
                for pattern in patterns:
                    for f in files:
                        if f == pattern:
                            mask_files.append(os.path.join(root, f))
                            break
                    if mask_files:
                        break
        
        if mask_files:
            mask_img = Image.open(mask_files[0]).convert('RGB')
            images.append(mask_img)
            
            # Create label
            if 'threshold' in test_name:
                parts = test_name.split('_')
                labels.append(f'T={parts[1]}')
            elif 'model' in test_name:
                parts = test_name.split('_')
                labels.append(f'M={parts[1]}')
            elif 'window' in test_name:
                parts = test_name.split('_')
                labels.append(f'W={parts[1]}')
            else:
                labels.append(test_name[:10])
    
    if len(images) <= 1:
        print(f'Error: Not enough images for frame {frame_num}')
        return False
    
    # Limit to 5 images max (original + 4 tests)
    if len(images) > 5:
        images = images[:5]
        labels = labels[:5]
    
    # Create horizontal layout (1 row, multiple columns)
    num_images = len(images)
    
    img_w, img_h = images[0].size
    label_h = 80  # Increased for better parameter display
    padding = 15
    title_h = 60
    
    # Calculate dimensions for horizontal layout
    grid_w = num_images * img_w + (num_images + 1) * padding
    grid_h = img_h + label_h + title_h + padding * 2
    
    grid = Image.new('RGB', (grid_w, grid_h), color=(245, 245, 245))
    draw = ImageDraw.Draw(grid)
    
    # Load fonts
    try:
        font_title = ImageFont.truetype('arial.ttf', 28)
        font_label = ImageFont.truetype('arial.ttf', 20)
        font_param = ImageFont.truetype('arialbd.ttf', 16)  # Bold for parameters
    except:
        font_title = ImageFont.load_default()
        font_label = font_title
        font_param = font_title
    
    # Draw title
    title = f'Frame {frame_num:05d} - Parameter Comparison'
    title_bbox = draw.textbbox((0, 0), title, font=font_title)
    title_w = title_bbox[2] - title_bbox[0]
    draw.text((grid_w // 2 - title_w // 2, 15), title, fill=(0, 0, 0), font=font_title)
    
    # Place images horizontally
    for idx, (img, label) in enumerate(zip(images, labels)):
        x = idx * (img_w + padding) + padding
        y = title_h
        
        # Paste image
        grid.paste(img, (x, y))
        
        # Draw label background with color coding
        label_y = y + img_h + 5
        
        # Color code by type
        if idx == 0:
            bg_color = (230, 230, 250)  # Light blue for original
            border_color = (100, 100, 200)
        elif 'T=' in label:
            bg_color = (255, 240, 245)  # Light pink for threshold
            border_color = (200, 100, 100)
        elif 'M=' in label:
            bg_color = (240, 255, 240)  # Light green for model
            border_color = (100, 200, 100)
        else:
            bg_color = (255, 255, 230)  # Light yellow for window
            border_color = (200, 200, 100)
        
        draw.rectangle([x, label_y, x + img_w, label_y + label_h], 
                      fill=bg_color, outline=border_color, width=2)
        
        # Draw label text (centered)
        label_bbox = draw.textbbox((0, 0), label, font=font_label)
        label_w = label_bbox[2] - label_bbox[0]
        text_x = x + (img_w - label_w) // 2
        draw.text((text_x, label_y + 10), label, fill=(0, 0, 0), font=font_label)
        
        # Add parameter description
        if idx == 0:
            param_text = "Source"
        elif 'T=' in label:
            threshold_val = label.split('=')[1]
            if threshold_val == '0.3':
                param_text = "Loose mask"
            elif threshold_val == '0.5':
                param_text = "Balanced"
            elif threshold_val == '0.7':
                param_text = "Strict mask"
            else:
                param_text = f"Threshold {threshold_val}"
        elif 'M=' in label:
            model = label.split('=')[1]
            if model == 'tiny':
                param_text = "Fast/Low Acc"
            elif model == 'base':
                param_text = "Balanced"
            elif model == 'large':
                param_text = "High Acc/Slow"
            else:
                param_text = f"Model {model}"
        elif 'W=' in label:
            window = label.split('=')[1]
            param_text = f"{window} frames"
        else:
            param_text = ""
        
        if param_text:
            param_bbox = draw.textbbox((0, 0), param_text, font=font_param)
            param_w = param_bbox[2] - param_bbox[0]
            param_x = x + (img_w - param_w) // 2
            draw.text((param_x, label_y + 45), param_text, fill=(60, 60, 60), font=font_param)
    
    grid.save(output_path, quality=95)
    print(f'Created: {os.path.basename(output_path)}')
    return True

# Main
if __name__ == '__main__':
    config_path = sys.argv[1]
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    test_dirs = config['test_dirs']
    frame_numbers = config['frame_numbers']
    output_dir = config['output_dir']
    source_frames_dir = config['source_frames_dir']
    
    print(f'Creating {len(frame_numbers)} comparisons...')
    print(f'Tests: {len(test_dirs)}')
    print(f'Source: {source_frames_dir}')
    print('')
    
    success = 0
    for frame_num in frame_numbers:
        output_path = os.path.join(output_dir, f'comparison_frame_{frame_num:05d}.png')
        if create_comparison(test_dirs, frame_num, output_path, source_frames_dir):
            success += 1
    
    print(f'\nSuccess: {success}/{len(frame_numbers)}')
    sys.exit(0 if success > 0 else 1)
