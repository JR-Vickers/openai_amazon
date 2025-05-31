import json
import re
from pathlib import Path
from openai import OpenAI
import base64
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_tile(tile_path, prompt, model="gpt-4-vision-preview"):
    image_base64 = image_to_base64(tile_path)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        max_tokens=300
    )
    
    return response.choices[0].message.content

def analyze_all_tiles(prompt="Is there a geoglyph in this image? If so, describe it."):
    """
    Analyze all PNG files in outputs/tiles directory and save results to JSON.
    
    Args:
        prompt (str): The prompt to use for analysis
    """
    # Create results directory if it doesn't exist
    results_dir = Path("outputs/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all PNG files
    tiles_dir = Path("outputs/tiles")
    png_files = list(tiles_dir.glob("*.png"))
    
    results = []
    
    for png_file in png_files:
        # Extract coordinates from filename
        match = re.search(r"tile_(-?\d+\.\d+)_(-?\d+\.\d+)\.png", png_file.name)
        if match:
            lat, lon = float(match.group(1)), float(match.group(2))
            
            # Analyze the tile
            analysis = analyze_tile(str(png_file), prompt)
            
            # Create result entry
            result = {
                "filename": png_file.name,
                "latitude": lat,
                "longitude": lon,
                "prompt": prompt,
                "analysis": analysis
            }
            
            results.append(result)
    
    # Save results to JSON
    output_file = results_dir / "tile_analysis_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    return results

if __name__ == "__main__":
    results = analyze_all_tiles()
    print(f"Analysis complete. Results saved to outputs/results/tile_analysis_results.json") 